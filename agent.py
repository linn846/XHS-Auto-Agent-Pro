import os
import json
import time
import shutil
from agent import generator_test,render_covers
from generator_test import load_products, generate_ai_content, generate_image
from render_covers import render_covers

def run_agent():
    print("\n" + "🚀" * 10 + " 小红书内容生成智能体启动 " + "🚀" * 10)
    
    # 1. 自动清理并准备提交所需的目录结构
    # 按照大赛要求，我们需要一个干净的 outputs 目录
    if os.path.exists("outputs"): 
        shutil.rmtree("outputs")
    os.makedirs("outputs/covers")
    print("✅ 已初始化 outputs/ 提交目录")

    # 2. 读取输入 (inputs.json)
    products = load_products("inputs.json")
    if not products:
        print("❌ 错误：未发现输入数据 inputs.json")
        return

    print(f"📊 发现 {len(products)} 个待处理产品，开始全自动流水线...")
    
    start_time = time.time()
    final_results = []

    # 3. 进入全自动生产线
    for i, product in enumerate(products):
        print(f"\n--- [正在处理第 {i+1}/{len(products)} 个：{product.name}] ---")
        
        try:
            # 步骤 A：大脑生成文案与素材 (Qwen-Max)
            text_res = generate_ai_content(product)
            
            # 步骤 B：画家生成纯净底图 (豆包-Seedream)
            # 💡 修复点：直接传递整个 product 对象，内部已改为使用 .selling_point
            img_url = generate_image(product)
            
            # 步骤 C：构建符合大赛格式的单条数据
            # 对应要求中的 product_id, cover, title, content, tags
            item_data = {
                "product_id": product.product_id,
                "cover": f"{product.product_id}_cover.png", # 预设文件名
                "title": text_res.title,
                "content": text_res.content,
                "tags": text_res.tags,
                # --- 以下是隐藏辅助字段，供 render_covers 使用 ---
                "product_name": product.name,
                "image_url": img_url,
                "tone": product.tone,
                "cover_title": text_res.cover_title,
                "features": text_res.ui_features, # 对应之前的 features
                "price": str(product.price)
            }
            final_results.append(item_data)
            
        except Exception as e:
            print(f"  ❌ 该产品处理失败: {e}")

    # 4. 保存中间数据到 outputs 目录，供渲染引擎使用
    # 注意：我们的 render_covers 现在需要读这个文件
    with open("outputs/results.json", "w", encoding="utf-8") as f:
        json.dump(final_results, f, ensure_ascii=False, indent=2)
    print("\n✅ 已生成中间数据并存入 outputs/results.json")

    # 5. 调用渲染引擎合成图片
    print("\n🎨 正在启动设计师渲染引擎，生成高清封面...")
    # 💡 确保 render_covers 内部逻辑已经适配从 outputs/results.json 读取
    render_covers() 
    
    # 6. 计算耗时
    total_duration = time.time() - start_time
    print("\n" + "="*50)
    print(f"🎉 Agent 任务全部圆满完成！")
    print(f"⏱️ 总计耗时：{total_duration:.1f} 秒")
    print(f"📂 作品已全部产出至：outputs/ 目录")
    print("="*50)
    print("💡 提示：提交前请确认 outputs/covers/ 下图片完整且无乱码。")

if __name__ == "__main__":
    run_agent()