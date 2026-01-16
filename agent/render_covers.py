import json
import os
import requests
import time
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import urllib3

# 1. 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- 2. 视觉规范配置 (莫兰迪设计师色系) ---
STYLE_CONFIG = {
    "温馨治愈": {"tag_text": (139, 69, 19), "sub_text": (197, 160, 89)}, # 棕+金
    "专业测评": {"tag_text": (15, 23, 42), "sub_text": (70, 130, 180)},  # 深蓝+冷蓝
    "简约高级": {"tag_text": (33, 33, 33), "sub_text": (160, 160, 160)}, # 黑+灰
    "活泼俏皮": {"tag_text": (255, 140, 0), "sub_text": (0, 128, 128)},  # 橙+绿
    "种草安利": {"tag_text": (178, 34, 34), "sub_text": (255, 36, 66)}   # 深红+亮红
}

def render_covers():
    print("\n" + "="*20 + " 🚀 渲染引擎：提交规格模式 " + "="*20)
    
    # --- [路径适配] ---
    # 大赛要求所有输出都在 outputs 目录下
    input_json_path = "outputs/results.json"
    output_dir = "outputs/covers"
    
    if not os.path.exists(output_dir): 
        os.makedirs(output_dir)
        print(f"📁 已准备输出目录: {output_dir}")

    if not os.path.exists(input_json_path):
        print(f"❌ 错误：找不到输入文件 {input_json_path}，请先运行 generator_test.py")
        return
        
    with open(input_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # --- [字体配置] ---
    font_path = "font.ttf"
    if not os.path.exists(font_path):
        print("❌ 错误：当前目录下找不到 font.ttf")
        return

    title_font = ImageFont.truetype(font_path, 90)  # 封面主标题
    tag_font = ImageFont.truetype(font_path, 42)    # 封面副标题
    price_font = ImageFont.truetype(font_path, 120) # 底部价格

    # 高级感背景色：奶油白
    CREAM_WHITE = (252, 251, 248) 

    print(f"📊 准备渲染 {len(data)} 张符合规范的封面...")

    for item in data:
        try:
            p_id = item.get('product_id', 'unknown')
            # 兼容处理：在 generator_test 中我们存的是 product_name
            p_name = item.get('product_name', '未命名产品')
            img_url = item.get('image_url')

            print(f"📸 正在处理: [{p_id}] {p_name}")
            
            # A. 下载豆包生出的底图
            resp = requests.get(img_url, timeout=60, verify=False)
            raw_img = Image.open(BytesIO(resp.content)).convert("RGBA")

            # --- [1. 智能比例适配：1:1 -> 3:4 拒绝变形] ---
            # 创建 1080x1440 奶油色大画布
            canvas = Image.new('RGBA', (1080, 1440), (*CREAM_WHITE, 255))
            
            # 缩放底图至 1080 宽
            img_w, img_h = 1080, 1080
            resized_product = raw_img.resize((img_w, img_h), Image.Resampling.LANCZOS)
            
            # 将产品放置在底部 (1440 - 1080 = 360 留白给顶部)
            canvas.paste(resized_product, (0, 360), resized_product)
            img = canvas

            # --- [2. 绘制自然渐变消融层] ---
            overlay = Image.new('RGBA', img.size, (0,0,0,0))
            draw_ov = ImageDraw.Draw(overlay)
            fade_start, fade_height = 360, 250 
            for y in range(fade_height):
                alpha = int(255 * (1 - (y / fade_height)))
                draw_ov.line([(0, fade_start + y), (1080, fade_start + y)], fill=(*CREAM_WHITE, alpha))

            # --- [3. 居中排版：大牌氛围感] ---
            MAIN_TEXT_COLOR = (26, 35, 126) # 深藏青
            cfg = STYLE_CONFIG.get(item.get('tone'), STYLE_CONFIG["温馨治愈"])
            draw = ImageDraw.Draw(img)

            # 主标题居中 (AI 生成的 cover_title)
            main_title = item.get('cover_title', "精选单品")
            t_bbox = draw.textbbox((0, 0), main_title, font=title_font)
            draw.text(((1080 - (t_bbox[2]-t_bbox[0])) // 2, 130), main_title, font=title_font, fill=(*MAIN_TEXT_COLOR, 255))

            # 副标题居中 (取 features 列表中的第一项)
            features = item.get('features', ["品质生活"])
            # 确保 features 是列表且不为空
            sub_title = features[0] if isinstance(features, list) and len(features) > 0 else "必入好物"
            sub_title = sub_title.replace("✅", "").strip() # 清理可能残留的符号
            
            s_bbox = draw.textbbox((0, 0), sub_title, font=tag_font)
            draw.text(((1080 - (s_bbox[2]-s_bbox[0])) // 2, 260), sub_title, font=tag_font, fill=(*cfg['sub_text'], 255))

            # 价格居中 (来自 generator_test 估算的 price)
            price_str = f"¥{item.get('price', '299')}"
            p_bbox = draw.textbbox((0, 0), price_str, font=price_font)
            draw.text(((1080 - (p_bbox[2]-p_bbox[0])) // 2, 1260), price_str, font=price_font, fill=(50, 50, 50, 255))

            # --- [4. 合成、转换并保存] ---
            final_img = Image.alpha_composite(img, overlay)
            
            # --- [输出规格适配] ---
            # 文件名要求：P001_cover.png
            save_filename = f"{p_id}_cover.png"
            save_path = os.path.join(output_dir, save_filename)
            
            final_img.convert("RGB").save(save_path, "PNG")
            print(f"  ✅ 成果已保存: {save_path}")

        except Exception as e:
            print(f"  ❌ 处理产品 {item.get('product_id', 'unknown')} 失败: {e}")

    print("\n" + "="*50)
    print("🎉 成果交付：所有 3:4 封面已生成至 outputs/covers/")
    print("="*50)

if __name__ == "__main__":
    render_covers()