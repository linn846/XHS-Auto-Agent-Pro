import os
import json
import time
import shutil
# 确保是从 agent 文件夹导入
from agent.generator_test import load_products, generate_ai_content, generate_image
from agent.render_covers import render_covers

def run_agent():
    # 增加一行启动日志，用来确认程序真的进来了
    print("\n" + "🚀" * 10 + " Agent 引擎正式启动 " + "🚀" * 10)
    
    # 1. 初始化目录
    if os.path.exists("outputs"): 
        shutil.rmtree("outputs")
    os.makedirs("outputs/covers")
    print("✅ 已清空并初始化 outputs/ 目录")

    # 2. 读取输入
    # 注意：此时 main.py 在根目录，它找同级目录下的 inputs.json
    products = load_products("inputs.json")
    if not products:
        print("❌ 错误：未发现 inputs.json 数据")
        return

    print(f"📊 发现 {len(products)} 个待处理产品...")
    
    start_time = time.time()
    final_results = []

    # 3. 生产线循环
    for product in products:
        try:
            print(f"\n--- 正在处理: {product.name} ---")
            # 调用 agent 文件夹内的逻辑
            text_res = generate_ai_content(product)
            img_url = generate_image(product)
            
            item_data = {
                "product_id": product.product_id,
                "cover": f"{product.product_id}_cover.png",
                "title": text_res.title,
                "content": text_res.content,
                "tags": text_res.tags,
                # 辅助绘图字段
                "product_name": product.name,
                "image_url": img_url,
                "tone": product.tone,
                "cover_title": text_res.cover_title,
                "features": text_res.ui_features,
                "price": str(product.price)
            }
            final_results.append(item_data)
        except Exception as e:
            print(f"❌ 运行中出错: {e}")

    # 4. 保存中间 JSON
    with open("outputs/results.json", "w", encoding="utf-8") as f:
        json.dump(final_results, f, ensure_ascii=False, indent=2)
    
    # 5. 调用渲染引擎
    print("\n🎨 正在执行视觉排版...")
    render_covers() 
    
    print(f"\n" + "="*40)
    print(f"🎉 任务圆满完成！耗时: {time.time() - start_time:.1f}s")
    print(f"📂 成果已保存至 outputs/ 目录")
    print("="*40)

# --- 🔥 这里就是“油门”：在函数外面、最底层调用 ---
if __name__ == "__main__":
    run_agent()