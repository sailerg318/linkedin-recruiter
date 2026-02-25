# LinkedIn人才搜索系统

自动化LinkedIn人才搜索和筛选工具，使用Tavily搜索引擎和飞书多维表格。

## 功能特点

✨ **智能搜索**
- 使用Tavily Web Search API搜索LinkedIn候选人
- 支持自定义岗位需求和关键词
- 自动提取候选人信息（姓名、职位、简介等）

🎯 **精细筛选**
- 多维度筛选条件（关键词、经验年限、地点、公司背景等）
- 可自定义筛选规则
- 智能去重，避免重复添加

📊 **飞书集成**
- 自动添加候选人到飞书多维表格
- 支持批量操作
- 实时同步数据

⏰ **定时任务**
- 每2分钟自动执行一轮搜索
- 每轮从10个候选人中筛选符合要求的
- 支持持续运行或指定轮数

## 安装

### 1. 克隆或下载项目

```bash
cd linkedin_recruiter
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置API密钥

编辑 [`config.py`](config.py:1) 文件，填入以下信息：

```python
# Tavily API配置
TAVILY_API_KEY = "your_tavily_api_key_here"

# 飞书多维表格配置
FEISHU_APP_ID = "your_feishu_app_id_here"
FEISHU_APP_SECRET = "your_feishu_app_secret_here"
FEISHU_TABLE_ID = "your_table_id_here"
FEISHU_TABLE_APP_TOKEN = "your_app_token_here"
```

#### 获取Tavily API密钥

1. 访问 [Tavily官网](https://tavily.com/)
2. 注册账号并获取API密钥

#### 获取飞书配置信息

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 获取 App ID 和 App Secret
4. 创建多维表格，获取 App Token 和 Table ID
5. 为应用添加权限：
   - `bitable:app`（多维表格应用权限）
   - `bitable:record`（记录读写权限）

## 使用方法

### 快速开始

编辑 [`main.py`](main.py:1) 中的配置：

```python
# 定义岗位需求
job_requirements = {
    "job_title": "Python Engineer",  # 岗位名称
    "keywords": "AI Machine Learning"  # 额外关键词
}

# 定义筛选条件
filter_requirements = {
    "required_keywords": ["Python", "AI"],  # 必须包含
    "exclude_keywords": ["intern", "实习"],  # 排除
    "min_score": 0.6,  # 最低相关度
    "min_experience": 3,  # 最少年限
}
```

### 运行程序

```bash
python main.py
```

### 运行模式

#### 模式1：单次运行（测试用）

```python
recruiter.run_single_search(job_requirements, filter_requirements)
```

#### 模式2：持续运行，指定轮数

```python
recruiter.run_continuous(job_requirements, filter_requirements, max_rounds=5)
```

#### 模式3：持续运行，直到手动停止

```python
recruiter.run_continuous(job_requirements, filter_requirements)
```

按 `Ctrl+C` 停止程序。

## 项目结构

```
linkedin_recruiter/
├── __init__.py              # 包初始化
├── config.py                # 配置文件
├── main.py                  # 主程序入口
├── tavily_search.py         # Tavily搜索模块
├── candidate_filter.py      # 候选人筛选模块
├── feishu_table.py          # 飞书表格集成
├── requirements.txt         # 依赖列表
└── README.md               # 项目文档
```

## 核心模块说明

### TavilySearcher

使用Tavily API搜索LinkedIn候选人。

```python
from tavily_search import TavilySearcher

searcher = TavilySearcher()
candidates = searcher.search_linkedin_candidates(
    job_title="Python Engineer",
    keywords="AI Machine Learning"
)
```

### CandidateFilter

根据条件筛选候选人。

```python
from candidate_filter import create_filter_from_requirements

filter_obj = create_filter_from_requirements({
    "required_keywords": ["Python"],
    "min_score": 0.7
})
filtered = filter_obj.filter_candidates(candidates)
```

### FeishuTableClient

飞书多维表格操作。

```python
from feishu_table import FeishuTableClient

client = FeishuTableClient()
client.add_records(candidates)
```

## 筛选条件说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `required_keywords` | List[str] | 必须包含的关键词 |
| `exclude_keywords` | List[str] | 排除的关键词 |
| `min_score` | float | 最低相关度分数（0-1） |
| `min_experience` | int | 最少工作年限 |
| `preferred_locations` | List[str] | 优选地点 |
| `preferred_companies` | List[str] | 优选公司 |

## 配置参数

在 [`config.py`](config.py:1) 中可调整：

```python
SEARCH_INTERVAL = 120  # 搜索间隔（秒）
BATCH_SIZE = 10        # 每批处理数量
MAX_SEARCH_RESULTS = 100  # 最大搜索结果数
```

## 飞书表格字段

程序会在飞书表格中创建以下字段：

- **姓名**: 候选人姓名
- **LinkedIn链接**: 个人主页URL
- **职位**: 当前或最近职位
- **简介**: 个人简介片段
- **相关度分数**: 与岗位的匹配度（0-1）
- **添加时间**: 记录添加时间戳

## 注意事项

⚠️ **重要提示**

1. 请遵守LinkedIn的使用条款和隐私政策
2. 合理设置搜索间隔，避免频繁请求
3. 妥善保管API密钥，不要提交到公开仓库
4. 建议使用环境变量或 `.env` 文件存储敏感信息

## 故障排查

### 问题1：Tavily搜索失败

- 检查API密钥是否正确
- 确认账户有足够的配额
- 检查网络连接

### 问题2：飞书表格添加失败

- 确认App ID和Secret正确
- 检查应用权限是否足够
- 验证Table ID和App Token

### 问题3：筛选结果为空

- 放宽筛选条件
- 检查关键词是否过于严格
- 调整相关度分数阈值

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至：your.email@example.com
