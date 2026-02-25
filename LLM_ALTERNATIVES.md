# LLM 替代方案

## 当前问题

`api.gemai.cc` 经常超时，导致 Pro 分析失败。

## 解决方案：切换 LLM 提供商

### 方案 1：使用 OpenAI（推荐）

**优势：**
- 稳定性高
- 速度快
- API 兼容性好

**配置步骤：**

1. 获取 OpenAI API Key
   - 访问 https://platform.openai.com/api-keys
   - 创建新的 API Key

2. 修改 `llm_config.py`：
```python
# OpenAI 配置
API_BASE = "https://api.openai.com/v1"
MODEL_NAME = "gpt-4o-mini"  # 或 "gpt-4o"
DEFAULT_KEY = "sk-your-openai-api-key"
```

### 方案 2：使用 DeepSeek

**优势：**
- 价格便宜
- 中文支持好
- 速度快

**配置步骤：**

1. 获取 DeepSeek API Key
   - 访问 https://platform.deepseek.com/
   - 注册并获取 API Key

2. 修改 `llm_config.py`：
```python
# DeepSeek 配置
API_BASE = "https://api.deepseek.com/v1"
MODEL_NAME = "deepseek-chat"
DEFAULT_KEY = "your-deepseek-api-key"
```

### 方案 3：使用 Claude（Anthropic）

**优势：**
- 分析能力强
- 上下文窗口大
- 安全性高

**配置步骤：**

1. 获取 Claude API Key
   - 访问 https://console.anthropic.com/
   - 创建 API Key

2. 修改 `llm_config.py`：
```python
# Claude 配置
API_BASE = "https://api.anthropic.com/v1"
MODEL_NAME = "claude-3-5-sonnet-20241022"
DEFAULT_KEY = "your-anthropic-api-key"
```

**注意：** Claude 的 API 格式略有不同，可能需要修改 `detailed_screening.py` 中的 `_call_llm` 方法。

### 方案 4：使用国内中转服务

如果无法直接访问国外 API，可以使用中转服务：

**常见中转服务：**
- https://api.openai-proxy.com
- https://api.openai-sb.com
- https://api.chatanywhere.com.cn

**配置示例：**
```python
API_BASE = "https://api.openai-proxy.com/v1"
MODEL_NAME = "gpt-4o-mini"
DEFAULT_KEY = "your-api-key"
```

## 当前配置文件位置

`linkedin_recruiter/llm_config.py`

## 修改后需要重启

修改配置后，需要重新运行程序：
```bash
python3 quick_run.py
```

## 推荐配置

**最佳性价比：**
```python
API_BASE = "https://api.deepseek.com/v1"
MODEL_NAME = "deepseek-chat"
```

**最佳稳定性：**
```python
API_BASE = "https://api.openai.com/v1"
MODEL_NAME = "gpt-4o-mini"
```

**最佳分析能力：**
```python
API_BASE = "https://api.openai.com/v1"
MODEL_NAME = "gpt-4o"
```

## 成本对比

| 提供商 | 模型 | 输入价格 | 输出价格 | 速度 |
|--------|------|----------|----------|------|
| OpenAI | gpt-4o-mini | $0.15/1M | $0.60/1M | 快 |
| OpenAI | gpt-4o | $2.50/1M | $10.00/1M | 中 |
| DeepSeek | deepseek-chat | ¥1/1M | ¥2/1M | 快 |
| Claude | claude-3-5-sonnet | $3.00/1M | $15.00/1M | 中 |

## 故障排查

如果切换后仍然失败：

1. 检查 API Key 是否正确
2. 检查网络连接
3. 检查 API 配额是否用完
4. 查看详细错误信息

## 临时解决方案

如果暂时无法切换 LLM，可以：

1. 只使用 Flash 筛选（跳过 Pro 分析）
2. 减少批次大小
3. 增加重试次数
4. 使用本地 JSON/Markdown 导出（不依赖 Pro 分析）
