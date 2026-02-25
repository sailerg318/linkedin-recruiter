# LinkedIn 招聘系统 - 完整使用指南

## 📋 目录

1. [系统概述](#系统概述)
2. [快速开始](#快速开始)
3. [核心功能](#核心功能)
4. [配置说明](#配置说明)
5. [使用方法](#使用方法)
6. [文件说明](#文件说明)
7. [常见问题](#常见问题)

---

## 系统概述

LinkedIn 招聘系统是一个智能化的候选人搜索和筛选工具，使用 AI 技术自动化招聘流程。

### 主要特性

- 🔍 **多引擎搜索** - 支持 Serper/Gemini/Tavily 三种搜索引擎
- 🤖 **AI 智能分析** - 自动解析需求、生成搜索策略
- 📊 **两阶段筛选** - Flash 快速筛选 + Pro 深度分析
- 🔄 **流式处理** - 边搜索边筛选边导出，内存高效
- 📈 **岗位扩展** - AI 自动生成岗位关键词变体
- 📍 **严格匹配** - 地点匹配只看当前位置
- 📤 **多格式导出** - JSON/Markdown/Google Sheets
- ☁️ **OAuth 认证** - 使用您自己的 Google Drive（2TB）

---

## 快速开始

### 1. 安装依赖

```bash
cd ~/Desktop/linkedin_recruiter
pip3 install -r requirements.txt
```

### 2. 配置 OAuth（首次使用）

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 启用 Google Sheets API 和 Drive API
3. 创建 OAuth 客户端凭证（桌面应用）
4. 下载凭证文件并重命名为 `oauth_credentials.json`
5. 放到 `linkedin_recruiter` 目录下

详细步骤见 [`OAUTH_SETUP.md`](OAUTH_SETUP.md)

### 3. 运行系统

```bash
python3 quick_run.py
```

首次运行会打开浏览器进行 OAuth 认证，授权后即可使用。

---

## 核心功能

### 1. 智能需求解析

系统自动分析招聘需求，提取关键信息：

```python
输入: "我想找 Base 上海的产品经理，5-8年经验，有大厂背景"

输出:
- 职位: Product Manager
- 地点: 上海
- 年限: 5-8年
- 背景: 大厂经验
```

### 2. 岗位关键词扩展

AI 自动生成岗位名称变体，扩大搜索范围：

```python
输入: "Product Manager"

输出:
- Product Manager
- PM
- Senior Product Manager
- Product Lead
- Product Owner
```

### 3. 多引擎搜索

**Serper 搜索（推荐）**
- 使用 Google 搜索
- 分页策略：每页 10 条，自动翻页
- 支持公司切片和字母切片

**Gemini 搜索**
- 使用 Google Grounding
- 不需要额外 API
- 结果质量高

**Tavily 搜索**
- 专业搜索 API
- 需要 Tavily API Key

### 4. 两阶段筛选

**Flash 粗筛（快速）**
- 模型：`[福利]gemini-3-flash-preview`
- 速度快，成本低
- 评分 0-100 分
- 默认阈值：50 分

**Pro 精筛（深度）**
- 模型：`[福利]gemini-3-flash-preview`
- 详细分析匹配度
- 生成推荐理由
- 默认阈值：70 分

### 5. 严格地点匹配

只看候选人的**当前所在地**，不考虑历史地点：

- ✅ 当前在伦敦 → 匹配
- ❌ 曾在伦敦，现在上海 → 不匹配

### 6. 流式处理

边搜索边筛选边导出，提升效率：

```
搜索 → Flash 筛选 → Pro 筛选 → 导出
  ↓         ↓           ↓         ↓
 实时     实时        实时      实时
```

### 7. 多格式导出

- **Google Sheets** - 在线协作，自动格式化
- **JSON** - 结构化数据，便于处理
- **Markdown** - 可读性强，便于查看

---

## 配置说明

### LLM 配置 (`llm_config.py`)

```python
# API 配置
API_BASE = "https://api.gemai.cc/v1"
MODEL_NAME = "[福利]gemini-3-flash-preview"
DEFAULT_KEY = "your-api-key"
```

**支持的模型：**
- `[福利]gemini-3-flash-preview` - Flash 模型（推荐）
- `[官逆]gemini-3-pro-preview` - Pro 模型
- `minimax-m2` - MiniMax 模型
- `gpt-4o-mini` - OpenAI 模型（需要切换 API_BASE）

### 搜索配置

**Serper API**
```python
SERPER_API_KEY = "d88085d4543221682eecd92082f27247f71d902f"
```

**搜索参数**
- `search_batch_size`: 搜索批次大小（默认 50）
- `screen_batch_size`: 筛选批次大小（默认 10）
- `flash_threshold`: Flash 阈值（默认 50）
- `pro_threshold`: Pro 阈值（默认 70）

### OAuth 配置

文件位置：
- `oauth_credentials.json` - OAuth 客户端凭证
- `token.pickle` - 访问令牌（自动生成）

---

## 使用方法

### 方式 1：快速运行（推荐）

```bash
python3 quick_run.py
```

交互式输入需求和配置参数。

### 方式 2：交互式菜单

```bash
python3 start.py
```

选择不同的功能模式。

### 方式 3：编程调用

```python
from streaming_pipeline import quick_streaming_pipeline

result = quick_streaming_pipeline(
    user_input="Base 上海的产品经理，5-8年经验",
    search_batch_size=50,
    screen_batch_size=10,
    flash_threshold=50,
    pro_threshold=70,
    engine="serper",
    share_emails=["colleague@example.com"]
)

print(f"找到 {result['pro_passed']} 位候选人")
print(f"Google Sheets: {result['url']}")
```

---

## 文件说明

### 核心模块

| 文件 | 说明 |
|------|------|
| [`unified_searcher.py`](unified_searcher.py) | 统一搜索器，整合多个搜索引擎 |
| [`detailed_screening.py`](detailed_screening.py) | 两阶段筛选（Flash + Pro） |
| [`streaming_pipeline.py`](streaming_pipeline.py) | 流式处理流水线 |
| [`requirement_parser.py`](requirement_parser.py) | 需求解析模块 |
| [`job_expander.py`](job_expander.py) | 岗位关键词扩展 |
| [`google_sheets_exporter.py`](google_sheets_exporter.py) | Google Sheets 导出（OAuth） |

### 搜索引擎

| 文件 | 说明 |
|------|------|
| [`serper_search.py`](serper_search.py) | Serper 搜索（分页策略） |
| [`gemini_search.py`](gemini_search.py) | Gemini 搜索（Grounding） |
| [`tavily_search.py`](tavily_search.py) | Tavily 搜索 |

### 启动脚本

| 文件 | 说明 |
|------|------|
| [`quick_run.py`](quick_run.py) | 快速运行脚本 |
| [`start.py`](start.py) | 交互式菜单 |
| [`recruiter_pro.py`](recruiter_pro.py) | 批量处理入口 |

### 配置文件

| 文件 | 说明 |
|------|------|
| [`llm_config.py`](llm_config.py) | LLM 配置 |
| [`config.py`](config.py) | 系统配置 |
| [`requirements.txt`](requirements.txt) | Python 依赖 |

### 文档

| 文件 | 说明 |
|------|------|
| [`README.md`](README.md) | 项目说明 |
| [`OAUTH_SETUP.md`](OAUTH_SETUP.md) | OAuth 设置指南 |
| [`OAUTH_QUICKSTART.md`](OAUTH_QUICKSTART.md) | OAuth 快速开始 |
| [`PROCESS_FLOW.md`](PROCESS_FLOW.md) | 流程说明 |
| [`API_USAGE.md`](API_USAGE.md) | API 使用说明 |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | 系统架构 |
| [`LLM_ALTERNATIVES.md`](LLM_ALTERNATIVES.md) | LLM 替代方案 |

---

## 常见问题

### Q1: OAuth 认证失败？

**解决方案：**
1. 检查 `oauth_credentials.json` 是否存在
2. 确认已启用 Google Sheets API 和 Drive API
3. 删除 `token.pickle` 重新认证

### Q2: Serper 搜索返回 400 错误？

**原因：** 单次请求结果数超过限制（免费版限制 10 条）

**解决方案：** 已实现分页策略，自动处理

### Q3: LLM API 超时？

**解决方案：**
1. 已增加超时时间到 60 秒
2. 已添加 3 次重试机制
3. 可切换到其他 LLM 提供商（见 [`LLM_ALTERNATIVES.md`](LLM_ALTERNATIVES.md)）

### Q4: 地点匹配不准确？

**解决方案：** 已修改 prompt，明确只看当前所在地

### Q5: 岗位扩展失败？

**解决方案：** 
1. 检查 LLM API 是否可用
2. 系统会自动回退到不扩展模式
3. 可以手动禁用：`enable_job_expansion=False`

### Q6: Google Sheets 创建失败？

**可能原因：**
1. OAuth 认证过期 - 删除 `token.pickle` 重新认证
2. API 格式错误 - 已修复
3. 网络问题 - 检查网络连接

### Q7: 如何批量处理多个职位？

```python
from recruiter_pro import LinkedInRecruiterPro

recruiter = LinkedInRecruiterPro()

jobs = [
    "上海的产品经理，5-8年经验",
    "北京的技术总监，10年以上经验",
    "深圳的设计师，3-5年经验"
]

for job in jobs:
    result = recruiter.search_and_screen(job)
    print(f"完成: {job}")
```

### Q8: 如何调整筛选阈值？

```python
result = quick_streaming_pipeline(
    user_input="...",
    flash_threshold=60,  # 提高 Flash 阈值
    pro_threshold=80     # 提高 Pro 阈值
)
```

---

## 性能优化建议

### 1. 搜索优化

- 使用岗位扩展增加覆盖面
- 调整 `search_batch_size` 控制单次搜索量
- 使用公司切片和字母切片提高精度

### 2. 筛选优化

- 调整阈值平衡质量和数量
- 使用 Flash 模型提高速度
- 批量处理减少 API 调用

### 3. 导出优化

- 使用流式处理减少内存占用
- 定期清理 Google Drive 空间
- 使用 JSON 格式便于后续处理

---

## 系统架构

```
用户输入
   ↓
需求解析 (RequirementParser)
   ↓
岗位扩展 (JobTitleExpander)
   ↓
多引擎搜索 (UnifiedSearcher)
   ├─ Serper (分页)
   ├─ Gemini (Grounding)
   └─ Tavily
   ↓
Flash 粗筛 (DetailedScreening)
   ↓
Pro 精筛 (DetailedScreening)
   ↓
多格式导出
   ├─ Google Sheets (OAuth)
   ├─ JSON
   └─ Markdown
```

---

## 技术栈

- **语言**: Python 3.8+
- **搜索**: Serper API, Google Gemini, Tavily
- **AI**: Gemini Flash/Pro 模型
- **存储**: Google Sheets (OAuth), JSON, Markdown
- **认证**: OAuth 2.0

---

## 更新日志

### v2.0 (2026-02-11)
- ✅ 添加 OAuth 认证支持
- ✅ 实现 Serper 分页策略
- ✅ 添加岗位关键词扩展
- ✅ 优化地点匹配逻辑
- ✅ 增加 LLM 超时和重试机制
- ✅ 统一使用 Flash 模型

### v1.0
- 基础搜索和筛选功能
- 服务账号 Google Sheets 导出
- 单引擎搜索

---

## 联系方式

- 用户邮箱: sailerg318@gmail.com
- 项目路径: ~/Desktop/linkedin_recruiter

---

## 许可证

本项目仅供内部使用。

---

**最后更新**: 2026-02-11
