# 品牌感 · 小红书全自动内容生成智能体 (AIGC Agent)

本项旨在构建一个具备“平面设计师审美”的 AI 智能体，能够将原始产品信息（JSON）一键转化为符合小红书爆款规范的**高清 3:4 品牌海报**及**高转化种草文案**。

.
├── agent/                  # [必填] 核心逻辑文件夹
│    ├── __init__.py        # 模块标识
│    ├── generator_test.py  # 负责调取 Qwen 和 豆包 接口
│    └── render_covers.py   # 负责 Pillow 高级视觉排版逻辑
├── main.py                 # [必填] 启动入口
├── requirements.txt        # [必填] 依赖包清单
├── inputs.json             # 输入文件：存放待处理的产品清单
├── font.ttf                # 字体库：确保中文显示美观
├── .env           # 配置模版（不含敏感 Key）
└── outputs/                # [成果目录]
      ├── results.json      # 最终生成的文案与结构化素材
      └── covers/           # 最终生成的 3:4 高清 PNG 封面


---

## 🌟 核心亮点

### 1. 工业级“图文分离”架构
项目放弃了 AI 直接生图带文字的不可控方案，采用 **Qwen-Max (大脑) + Doubao-Seedream (画家) + Pillow (排版引擎)** 的三层解耦架构。确保文字无乱码、排版 100% 像素级可控。

### 2. 设计师级视觉工程
*   **渐变消融技术 (Gradient Fade)**：自研线性 Alpha 渐变算法，消除文字区与实拍图之间的硬切边，实现如雾般丝滑的视觉转场。
*   **智能比例适配**：针对生图模型 1:1 输出的局限，通过“背景自动拾色填充”逻辑无缝扩展为 3:4 (1080x1440)，确保产品主体不产生拉伸变形。
*   **大牌配色规范**：内置“深藏青 + 香槟金”等莫兰迪配色矩阵，根据风格自动适配。

### 3. 全自动化泛化能力
系统具备自动特征提取能力，无需人工干预即可动态生成：
*   **封面短标题**：精简至 2-8 字，构建第一眼视觉钩子。
*   **胶囊卖点标签**：自动提取 3 项核心特征并进行图形化渲染。
*   **动态估价系统**：基于模型知识库自动识别并标注产品价格，增强导购真实感。

---

## 🛠️ 技术栈
*   **文案/素材模型**：`ali/qwen-max`
*   **图像生成模型**：`bytedance/doubao-seedream-4.0`
*   **渲染引擎**：`Pillow` (Python Imaging Library)
*   **数据校验**：`Pydantic` (保证数据流结构化稳定)

---

## 🚀 快速启动 (Reproduction Guide)
一定注意第三步正确配置
### 1. 环境准备
确保你的环境已安装 Python 3.10+。

### 2. 安装依赖
```bash
pip install -r requirements.txt
3. 配置文件
在项目根目录 .env 文件，填入您的 API 密钥：

OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://router.shengsuanyun.com/api/v1
DEFAULT_MODEL_NAME=ali/qwen3-max
4. 运行 Agent
code
Bash
python main.py
📂 目录结构说明
依据大赛要求，本项目采用核心代码与执行入口分离的结构：

code
Text
.
├── agent/                  # [必填] 核心逻辑文件夹
│    ├── __init__.py        # 模块标识
│    ├── generator_test.py  # 负责调取 Qwen 和 豆包 接口
│    └── render_covers.py   # 负责 Pillow 高级视觉排版逻辑
├── main.py                 # [必填] 启动入口
├── requirements.txt        # [必填] 依赖包清单
├── inputs.json             # 输入文件：存放待处理的产品清单
├── font.ttf                # 字体库：确保中文显示美观
├── .env           # 配置模版（不含敏感 Key）
└── outputs/                # [成果目录]
      ├── results.json      # 最终生成的文案与结构化素材
      └── covers/           # 最终生成的 3:4 高清 PNG 封面