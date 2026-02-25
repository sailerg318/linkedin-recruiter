# LinkedIn 端到端候选人挖掘系统

## 🎯 系统概述

这是一个融合 **AI 智能分析** + **Serper 微切片搜索** 的端到端 LinkedIn 候选人挖掘系统。

### 核心特性

- ✅ **Module A (AI Brain)**: 自动分析职位需求，提取关键词、地点、目标公司
- ✅ **Module B (Serper Hand)**: 利用 Serper.dev API 进行大规模微切片搜索
- ✅ **智能去重**: 基于 URL 的自动去重机制
- ✅ **高覆盖率**: 每次搜索返回 100 条结果，最大化单次产出

---

## 🏗️ 系统架构

```
用户输入 (自然语言 JD)
    ↓
Module A: AI 需求分析
    ├─ 提取核心关键词 (base_keyword)
    ├─ 识别目标地点 (location)
    └─ 生成目标公司列表 (30家)
    ↓
Module B: Serper 微切片搜索
    ├─ 阶段1: 公司切片 (30次搜索 × 100结果)
    ├─ 阶段2: 字母切片 (26次搜索 × 100结果)
    └─ 实时去重
    ↓
输出: 去重后的候选人列表
```

---

## 📦 文件说明

### 核心文件

- **`linkedin_end_to_end.py`**: 主系统文件
  - `analyze_requirements()`: Module A - AI 需求分析
  - `serper_micro_slicing()`: Module B - 微切片搜索
  - `end_to_end_search()`: 端到端主函数

- **`test_end_to_end.py`**: 测试套件
  - 测试 AI 分析模块
  - 测试端到端搜索
  - 测试去重功能

---

## 🚀 快速开始

### 1. 配置 API Keys

在 [`linkedin_end_to_end.py`](linkedin_end_to_end.py:14) 中配置：

```python
# Serper API Key
SERPER_API_KEY = "your_serper_key_here"

# LLM API Key (已配置 Gemini)
LLM_API_KEY = DEFAULT_KEY  # 从 llm_config.py 导入
```

### 2. 直接运行

```bash
cd linkedin_recruiter
python linkedin_end_to_end.py
```

### 3. 使用测试套件

```bash
python test_end_to_end.py
```

---

## 💡 使用示例

### 示例 1: 组织发展顾问

```python
from linkedin_end_to_end import end_to_end_search

user_input = "我想找 Base 伦敦的 Org Development 顾问，7-15年经验，有咨询背景的"
candidates = end_to_end_search(user_input)

print(f"找到 {len(candidates)} 位候选人")
```

**AI 分析输出**:
```json
{
  "base_keyword": "Org Development",
  "location": "London",
  "target_companies": [
    "McKinsey", "BCG", "Bain", "Deloitte", "PwC", 
    "EY", "KPMG", "Accenture", ...
  ]
}
```

**搜索策略**:
- 公司切片: `site:linkedin.com/in/ "Org Development" "London" "McKinsey" -intitle:jobs`
- 字母切片: `site:linkedin.com/in/ "Org Development" "London" intitle:a -intitle:jobs`

---

### 示例 2: 算法交易员

```python
user_input = "寻找纽约的算法交易员，5年以上经验，来自顶级投行或对冲基金"
candidates = end_to_end_search(user_input)
```

**AI 分析输出**:
```json
{
  "base_keyword": "Algorithmic Trader",
  "location": "New York",
  "target_companies": [
    "Goldman Sachs", "Morgan Stanley", "Citadel", 
    "Jane Street", "Two Sigma", ...
  ]
}
```

---

### 示例 3: 电商运营

```python
user_input = "上海的电商运营专家，3-8年经验，有大厂背景"
candidates = end_to_end_search(user_input)
```

**AI 分析输出**:
```json
{
  "base_keyword": "E-commerce Operations",
  "location": "Shanghai",
  "target_companies": [
    "Alibaba", "Tencent", "ByteDance", "Pinduoduo",
    "JD.com", "Meituan", ...
  ]
}
```

---

## 🔧 核心函数详解

### Module A: `analyze_requirements(user_input)`

**功能**: 使用 LLM 分析自然语言需求

**输入**:
```python
user_input = "我想找 Base 伦敦的 OD，7-15年经验，甲乙方背景的"
```

**输出**:
```python
{
  "base_keyword": "Org Development",
  "location": "London",
  "target_companies": ["McKinsey", "BCG", "Bain", ...]
}
```

**特点**:
- 自动提取核心职位词（英文）
- 识别目标地点
- 根据行业智能生成 30 家目标公司

---

### Module B: `serper_micro_slicing(analysis_result)`

**功能**: 执行微切片大规模搜索

**搜索策略**:

1. **公司切片** (30 次搜索)
   ```
   site:linkedin.com/in/ "{keyword}" "{location}" "{company}" -intitle:jobs
   ```

2. **字母切片** (26 次搜索)
   ```
   site:linkedin.com/in/ "{keyword}" "{location}" intitle:{char} -intitle:jobs
   ```

**Serper 配置**:
```python
payload = {
    'q': query,
    'num': 100,      # 每次返回 100 条结果
    'gl': 'cn',      # 地区: 中国
    'hl': 'zh-cn'    # 语言: 简体中文
}
```

**去重机制**:
- 使用 `set()` 存储已见过的 URL
- 实时过滤重复候选人

---

## 📊 性能指标

### 搜索规模

- **公司切片**: 30 家公司 × 100 结果 = 最多 3,000 条
- **字母切片**: 26 个字母 × 100 结果 = 最多 2,600 条
- **理论最大**: 5,600 条候选人（去重后）

### 时间成本

- 单次搜索: ~1 秒
- 总搜索次数: 56 次 (30 + 26)
- 预计总时间: ~1-2 分钟

### API 成本

- Serper API: $5/1000 次搜索
- 单次完整搜索: 56 次 × $0.005 = **$0.28**

---

## ⚠️ 注意事项

### 1. API 限流

Serper API 有速率限制，代码中已添加 `time.sleep(0.5)` 避免过快请求。

### 2. LLM 稳定性

如果 LLM 返回格式错误，系统会：
- 尝试从 markdown 代码块中提取 JSON
- 使用正则表达式查找 JSON 对象
- 失败时返回默认值

### 3. 去重逻辑

基于 URL 去重，确保同一个 LinkedIn 个人主页不会重复出现。

---

## 🧪 测试

### 运行测试套件

```bash
python test_end_to_end.py
```

### 测试选项

1. **测试 AI 需求分析模块** - 验证 LLM 解析能力
2. **测试端到端搜索 - 简单案例** - 快速验证
3. **测试端到端搜索 - 完整案例** - 完整流程测试
4. **测试去重功能** - 验证去重机制
5. **运行所有测试** - 完整测试套件

---

## 📈 优化建议

### 1. 并行搜索

当前是串行搜索，可以使用 `concurrent.futures` 并行化：

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(_serper_search, query) for query in queries]
    results = [f.result() for f in futures]
```

### 2. 缓存机制

添加搜索结果缓存，避免重复搜索：

```python
import hashlib
import pickle

def cache_search(query):
    cache_key = hashlib.md5(query.encode()).hexdigest()
    cache_file = f"cache/{cache_key}.pkl"
    
    if os.path.exists(cache_file):
        return pickle.load(open(cache_file, 'rb'))
    
    results = _serper_search(query)
    pickle.dump(results, open(cache_file, 'wb'))
    return results
```

### 3. 动态切片

根据前几次搜索的结果数量，动态调整后续搜索策略。

---

## 🔗 相关文件

- [`serper_search.py`](serper_search.py:1) - Serper 搜索基础模块
- [`requirement_parser.py`](requirement_parser.py:1) - 需求解析模块
- [`llm_config.py`](llm_config.py:1) - LLM 配置

---

## 📝 更新日志

### v1.0.0 (2026-02-11)

- ✅ 实现 Module A: AI 需求分析
- ✅ 实现 Module B: Serper 微切片搜索
- ✅ 添加去重机制
- ✅ 创建测试套件
- ✅ 完善文档

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License
