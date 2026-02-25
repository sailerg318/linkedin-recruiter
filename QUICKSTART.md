# 快速入门指南

## 5分钟快速开始

### 第一步：安装依赖

```bash
cd linkedin_recruiter
pip install -r requirements.txt
```

### 第二步：配置API密钥

编辑 [`config.py`](config.py:1)，填入你的API密钥：

```python
TAVILY_API_KEY = "tvly-xxxxx"  # 你的Tavily API密钥
FEISHU_APP_ID = "cli_xxxxx"    # 你的飞书App ID
FEISHU_APP_SECRET = "xxxxx"    # 你的飞书App Secret
FEISHU_TABLE_APP_TOKEN = "xxxxx"  # 多维表格App Token
FEISHU_TABLE_ID = "xxxxx"      # 多维表格Table ID
```

### 第三步：运行程序

#### 方式1：使用交互式启动脚本（推荐）

```bash
python run.py
```

按照提示输入岗位需求和筛选条件即可。

#### 方式2：直接运行主程序

编辑 [`main.py`](main.py:1) 中的配置，然后运行：

```bash
python main.py
```

#### 方式3：运行示例

```bash
python examples.py
```

选择预设的示例场景。

---

## 获取API密钥

### Tavily API密钥

1. 访问 https://tavily.com/
2. 注册账号
3. 在Dashboard中获取API Key

### 飞书配置

#### 1. 创建飞书应用

1. 访问 https://open.feishu.cn/
2. 点击"创建企业自建应用"
3. 填写应用信息
4. 获取 **App ID** 和 **App Secret**

#### 2. 添加应用权限

在应用管理页面，添加以下权限：

- `bitable:app` - 多维表格应用权限
- `bitable:record` - 记录读写权限

点击"发布版本"使权限生效。

#### 3. 创建多维表格

1. 在飞书中创建一个多维表格
2. 添加以下字段：
   - **姓名** (文本)
   - **LinkedIn链接** (URL)
   - **职位** (文本)
   - **简介** (多行文本)
   - **相关度分数** (数字)
   - **添加时间** (日期)

3. 获取表格信息：
   - 打开表格，URL格式为：`https://xxx.feishu.cn/base/APP_TOKEN?table=TABLE_ID`
   - **APP_TOKEN**: base/ 后面的部分
   - **TABLE_ID**: table= 后面的部分

#### 4. 将应用添加到表格

1. 打开多维表格
2. 点击右上角"..."
3. 选择"高级设置" → "添加应用"
4. 选择你创建的应用

---

## 配置示例

### 搜索Python工程师

```python
job_requirements = {
    "job_title": "Python Engineer",
    "keywords": "AI Machine Learning"
}

filter_requirements = {
    "required_keywords": ["Python", "AI"],
    "min_score": 0.7,
    "min_experience": 3
}
```

### 搜索产品经理

```python
job_requirements = {
    "job_title": "Product Manager",
    "keywords": "SaaS B2B"
}

filter_requirements = {
    "required_keywords": ["Product"],
    "preferred_locations": ["San Francisco", "New York"],
    "min_score": 0.65
}
```

### 搜索中国市场候选人

```python
job_requirements = {
    "job_title": "Python工程师",
    "keywords": "人工智能 机器学习"
}

filter_requirements = {
    "required_keywords": ["Python"],
    "preferred_locations": ["北京", "上海", "深圳"],
    "preferred_companies": ["阿里巴巴", "腾讯", "字节跳动"],
    "min_score": 0.65
}
```

---

## 运行模式

### 单次运行（测试）

```python
recruiter.run_single_search(job_requirements, filter_requirements)
```

适合测试配置是否正确。

### 持续运行（指定轮数）

```python
recruiter.run_continuous(job_requirements, filter_requirements, max_rounds=5)
```

运行5轮后自动停止。

### 持续运行（无限）

```python
recruiter.run_continuous(job_requirements, filter_requirements)
```

持续运行，按 `Ctrl+C` 停止。

---

## 常见问题

### Q: Tavily搜索没有结果？

A: 
- 检查岗位名称是否太具体
- 尝试使用英文岗位名称
- 减少关键词数量

### Q: 飞书表格添加失败？

A:
- 确认应用已添加到表格
- 检查应用权限是否正确
- 验证Table ID和App Token

### Q: 筛选结果太少？

A:
- 降低 `min_score` 阈值
- 减少 `required_keywords`
- 降低 `min_experience` 要求

### Q: 如何调整搜索间隔？

A: 编辑 [`config.py`](config.py:1)：

```python
SEARCH_INTERVAL = 300  # 改为5分钟
```

---

## 下一步

- 查看 [README.md](README.md:1) 了解完整功能
- 运行 [examples.py](examples.py:1) 查看更多示例
- 阅读源码了解实现细节

---

## 技术支持

遇到问题？

1. 查看 [README.md](README.md:1) 的故障排查部分
2. 运行测试：`python test_modules.py`
3. 提交Issue到GitHub

祝你招聘顺利！🎉

