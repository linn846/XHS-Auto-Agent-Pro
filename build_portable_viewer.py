import json
import base64
import os

def build():
    json_path = "outputs/results.json"
    
    # --- 诊断 1：检查文件是否存在 ---
    if not os.path.exists(json_path):
        print(f"❌ 致命错误：找不到 {json_path}。请确认你先运行了 python agent.py")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except:
            print("❌ 致命错误：results.json 格式损坏，无法解析")
            return

    # --- 诊断 2：检查数据量 ---
    if not data or len(data) == 0:
        print("❌ 警告：results.json 是空的 []。说明 Agent 运行过程中可能报错跳过了所有产品。")
        return
    
    print(f"📊 诊断报告：发现 {len(data)} 条笔记数据。开始打包图片...")

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI 作品最终预览</title>
        <meta charset="UTF-8">
        <style>
            body { font-family: sans-serif; background: #f0f2f5; padding: 20px; }
            .card { background: white; border-radius: 12px; margin-bottom: 30px; display: flex; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); max-width: 900px; margin: 20px auto; }
            .cover { width: 400px; flex-shrink: 0; background: #ddd; }
            .cover img { width: 100%; display: block; }
            .content { padding: 30px; flex-grow: 1; }
            h2 { color: #333; margin-top: 0; }
            p { white-space: pre-wrap; color: #666; line-height: 1.6; }
            .tags { color: #ff2442; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1 style='text-align:center;'>智能体生成结果预览</h1>
        {cards}
    </body>
    </html>
    """

    cards_html = ""
    for idx, item in enumerate(data):
        # 兼容性读取：如果 Key 不叫 cover，尝试获取 product_id 拼凑
        img_filename = item.get('cover', f"{item.get('product_id')}_cover.png")
        img_path = os.path.join("outputs/covers", img_filename)
        
        img_base64 = ""
        if os.path.exists(img_path):
            with open(img_path, "rb") as image_file:
                img_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            print(f"  ✅ 第 {idx+1} 个产品：图片已嵌入 ({img_filename})")
        else:
            print(f"  ⚠️ 第 {idx+1} 个产品：找不到本地图片文件 ({img_path})")

        # 读取文字内容
        title = item.get('title', '【未生成标题】')
        content = item.get('content', '【未生成正文内容】')
        tags = item.get('tags', [])
        tag_str = " ".join([f"#{t}" for t in tags])
        
        img_src = f"data:image/png;base64,{img_base64}" if img_base64 else ""
        
        card = f"""
        <div class="card">
            <div class="cover">
                <img src="{img_src}" alt="图片未找到">
            </div>
            <div class="content">
                <h2>{title}</h2>
                <p>{content}</p>
                <div class="tags">{tag_str}</div>
            </div>
        </div>
        """
        cards_html += card

    final_html = html_template.replace("{cards}", cards_html)
    
    with open("portable_viewer.html", "w", encoding="utf-8") as f:
        f.write(final_html)
    print(f"\n✨ 预览包已重新生成：portable_viewer.html")

if __name__ == "__main__":
    build()