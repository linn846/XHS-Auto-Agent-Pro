import os
import json
import time
import requests
from typing import List, Optional, Any
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

# --- 1. 输入数据模型 (匹配 inputs.json) ---
class Product(BaseModel):
    product_id: str
    name: str
    category: str
    price: Any
    target_audience: str
    features: List[str]
    selling_point: str
    tone: str

# --- 2. AI 生成素材模型 ---
class GeneratedContent(BaseModel):
    cover_title: str = Field(description="2-8字的封面短标题")
    ui_features: List[str] = Field(description="3个不带Emoji的极短卖点标签")
    title: str = Field(description="正文标题")
    content: str = Field(description="种草正文")
    tags: List[str] = Field(description="话题标签列表") # 对齐输出格式中的 tags

def load_products(file_path: str = "inputs.json") -> List[Product]:
    if not os.path.exists(file_path):
        print(f"❌ 找不到输入文件: {file_path}")
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [Product(**item) for item in data]

# --- 3. 文案与视觉素材生成 (Qwen-Max) ---
def generate_ai_content(product: Product) -> GeneratedContent:
    start_time = time.time() 
    model_name = os.getenv("DEFAULT_MODEL_NAME", "ali/qwen3-max")
    
    print(f"\n✍️ 正在调用 [{model_name}] 生成爆款素材: [{product.name}]...")
    
    # 整合产品特征为 Prompt 字符串
    features_str = "、".join(product.features)
    
    system_prompt = f"""
    你是一名顶级小红书运营专家和视觉设计师。
    请根据产品信息，创作出极具吸引力的视觉素材和种草文案。
    必须返回一个合法的 JSON 格式，包含以下字段：
    1. "cover_title": 极简封面短标题，2-8个字（如：深睡神器、口袋里的键盘）。
    2. "ui_features": 列表，包含3个核心卖点文字，每项不超10字。严禁包含Emoji，直接输出纯文字（如：云朵般的睡眠体验）。
    3. "title": 爆款笔记正文标题（带Emoji）。
    4. "content": 笔记正文，口语化，多用“姐妹们”、“绝了”等语境，Emoji 丰富。
    5. "tags": 4个相关话题标签（不带#号，如：睡眠神器）。

    当前风格要求：{product.tone}
    """
    
    user_prompt = f"""
    产品名称：{product.name}
    品类：{product.category}
    价格：{product.price}
    受众：{product.target_audience}
    特征：{features_str}
    核心卖点：{product.selling_point}
    """
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            response_format={ "type": "json_object" }
        )
        
        raw_content = response.choices[0].message.content.strip()
        data = json.loads(raw_content)
        
        duration = time.time() - start_time
        print(f"[{time.strftime('%H:%M:%S')}] Step 1: 文案生成完成，耗时 {duration:.1f}s")
        return GeneratedContent(**data)
        
    except Exception as e:
        print(f"❌ Qwen 生成异常: {e}")
        return GeneratedContent(
            cover_title="精选好物", ui_features=["品质保证", "值得入手"],
            title="发现一款宝藏单品！", content="真的太好用了！", tags=["好物推荐"]
        )

# --- 4. 图像生成 (豆包) ---
def generate_image(product: Product) -> str:
    image_process_start = time.time()
    print(f"🎨 正在调用 [豆包-Seedream] 生图: [{product.name}]...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    base_api_url = "https://router.shengsuanyun.com/api/v1"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # 风格映射
    STYLE_PROMPTS = {
        "温馨治愈": "柔和奶油色调，温馨家居背景",
        "活泼俏皮": "鲜艳色彩，高饱和度，活力十足",
        "专业测评": "影棚灯光，极简科技背景，锐利细节",
        "种草安利": "高对比度，商业静物摄影，诱人质感",
        "简约高级": "极简主义，禅意留白，高级质感"
    }
    
    clean_prompt = f"产品摄影，{product.name}，{product.selling_point}，{STYLE_PROMPTS.get(product.tone, '')}。 " \
                   f"要求：POV第一视角，真实感，画面无任何文字，无LOGO，无水印，干净背景，4k。"

    payload = {
        "model": "bytedance/doubao-seedream-4.0",
        "prompt": clean_prompt,
        "size": "1024x1024",
        "watermark": False,
        "response_modalities": ["IMAGE"]
    }

    try:
        res = requests.post(f"{base_api_url}/tasks/generations", headers=headers, json=payload, timeout=30).json()
        request_id = res["data"]["request_id"]
        print(f"[{time.strftime('%H:%M:%S')}] Step 2: 图像任务提交成功 ID: {request_id}")

        for i in range(25): 
            time.sleep(4)
            query_res = requests.get(f"{base_api_url}/tasks/generations/{request_id}", headers=headers, timeout=30).json()
            status = query_res.get("data", {}).get("status")
            print(f"   [轮询] 状态: {status}")

            if status in ["SUCCESS", "COMPLETED"]:
                # 递归查找 URL
                def find_url(obj):
                    if isinstance(obj, str) and obj.startswith('http') and "placeholder" not in obj: return obj
                    if isinstance(obj, dict):
                        for v in obj.values():
                            res = find_url(v)
                            if res: return res
                    if isinstance(obj, list):
                        for item in obj:
                            res = find_url(item)
                            if res: return res
                    return None
                
                img_url = find_url(query_res)
                if img_url:
                    print(f"[{time.strftime('%H:%M:%S')}] Step 3: 生图获取成功，耗时 {time.time()-image_process_start:.1f}s")
                    return img_url
            
            if status in ["FAILED", "CANCELLED"]: break
        return "https://via.placeholder.com/1024"
    except Exception as e:
        print(f"❌ 图像生成异常: {e}")
        return "https://via.placeholder.com/1024"

# --- 5. 主函数：整合 Agent 输出 ---
def main():
    # 初始化目录
    if not os.path.exists("outputs/covers"):
        os.makedirs("outputs/covers")

    products = load_products("inputs.json")
    if not products: return

    # 比赛测试：处理所有产品
    results = []
    for product in products:
        print(f"\n🚀 Agent 开始处理产品: {product.product_id}")
        
        # A. 大脑生成
        ai_data = generate_ai_content(product)
        
        # B. 画家生成
        img_url = generate_image(product)
        
        # C. 对齐大赛输出格式
        results.append({
            "product_id": product.product_id,
            "cover": f"{product.product_id}_cover.png", # 对应生成的图片文件名
            "title": ai_data.title,
            "content": ai_data.content,
            "tags": ai_data.tags,
            # 以下字段保留，供 render_covers.py 绘图使用，最终提交前可选择性在JSON中保留
            "image_url": img_url,
            "price": str(product.price),
            "cover_title": ai_data.cover_title,
            "features": ai_data.ui_features, 
            "tone": product.tone
        })

    with open("outputs/results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*40)
    print("🎉 Agent 任务完成！")
    print("📁 结果已存入 outputs/results.json")
    print("💡 接下来请运行 render_covers.py 生成图片到 outputs/covers/")
    print("="*40)

if __name__ == "__main__":
    main()