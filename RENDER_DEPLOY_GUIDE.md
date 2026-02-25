# Render 部署完整指南

## 🚨 问题诊断

如果 Render 没有运行，可能的原因：

### 1. 服务未创建或未启动
- 检查 Render Dashboard 是否有服务
- 查看服务状态（Building / Live / Failed）

### 2. 构建失败
- 查看 Render 日志中的错误信息
- 常见问题：依赖安装失败、Python 版本不匹配

### 3. 启动失败
- 端口配置错误
- 缺少环境变量
- 代码运行时错误

---

## 📋 完整部署步骤

### 步骤 1: 准备 GitHub 仓库

✅ 已完成 - 代码已推送到：
```
https://github.com/sailerg318/linkedin-recruiter
```

关键文件：
- ✅ [`Procfile`](Procfile:1) - 启动命令
- ✅ [`runtime.txt`](runtime.txt:1) - Python 版本
- ✅ [`requirements.txt`](requirements.txt:1) - 依赖包

### 步骤 2: 创建 Render 服务

1. **访问 Render**
   - 打开 https://render.com
   - 登录或注册账号

2. **创建新服务**
   - 点击 "New +" → "Web Service"
   - 选择 "Connect a repository"

3. **连接 GitHub**
   - 授权 Render 访问 GitHub
   - 选择仓库：`sailerg318/linkedin-recruiter`

4. **配置服务**
   ```
   Name: linkedin-recruiter
   Region: Singapore (或其他区域)
   Branch: main
   Root Directory: (留空)
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python web_server.py
   ```

5. **选择计划**
   - Free（免费版）
   - 注意：15 分钟无活动后会休眠

### 步骤 3: 配置环境变量

在 Render Dashboard 的 "Environment" 标签页添加：

**必需的环境变量：**
```bash
SERPER_API_KEY=你的_serper_api_key
GEMINI_API_KEY=你的_gemini_api_key
```

**可选的环境变量：**
```bash
DEBUG=False
TAVILY_API_KEY=你的_tavily_api_key（如果使用）
```

⚠️ **重要**：不要设置 `PORT` 变量，Render 会自动设置

### 步骤 4: 部署

1. 点击 "Create Web Service"
2. 等待构建和部署（约 2-5 分钟）
3. 查看日志确认状态

---

## 🔍 故障排查

### 问题 1: 构建失败

**症状**：Build 阶段失败

**检查日志中的错误**：
```bash
# 常见错误 1: Python 版本不支持
ERROR: Could not find a version that satisfies the requirement...

# 解决方案：检查 runtime.txt
cat runtime.txt
# 应该是: python-3.13.0
```

```bash
# 常见错误 2: 依赖安装失败
ERROR: No matching distribution found for...

# 解决方案：检查 requirements.txt
```

### 问题 2: 启动失败

**症状**：Build 成功但服务无法启动

**检查启动日志**：
```bash
# 错误示例 1: 端口绑定失败
OSError: [Errno 98] Address already in use

# 解决方案：确保 web_server.py 使用环境变量 PORT
PORT = int(os.getenv('PORT', 3000))
app.run(host='0.0.0.0', port=PORT)
```

```bash
# 错误示例 2: 缺少环境变量
KeyError: 'SERPER_API_KEY'

# 解决方案：在 Render Dashboard 添加环境变量
```

### 问题 3: 服务运行但无法访问

**症状**：服务显示 "Live" 但打开 URL 报错

**检查**：
1. 确认服务 URL（格式：`https://your-service.onrender.com`）
2. 查看 Render 日志中的请求记录
3. 检查防火墙或网络问题

---

## 🧪 本地测试

在部署前，先在本地测试：

```bash
# 1. 进入项目目录
cd ~/Desktop/linkedin_recruiter

# 2. 安装依赖
pip install -r requirements.txt

# 3. 设置环境变量
export SERPER_API_KEY="你的key"
export GEMINI_API_KEY="你的key"
export PORT=3000

# 4. 启动服务
python web_server.py

# 5. 测试访问
open http://localhost:3000
```

如果本地运行正常，说明代码没问题，部署问题在配置。

---

## 📊 查看 Render 日志

### 实时日志
1. 进入 Render Dashboard
2. 选择你的服务
3. 点击 "Logs" 标签
4. 查看实时输出

### 关键日志信息

**成功启动的日志应该包含**：
```
==> Building...
Installing dependencies from requirements.txt
Successfully installed flask-3.0.0 ...

==> Starting service...
======================================================================
LinkedIn 招聘系统 - Web 服务
======================================================================

启动信息:
  - 端口: 10000
  - 调试模式: False

按 Ctrl+C 停止服务
======================================================================

 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:10000
 * Running on http://10.x.x.x:10000
```

**如果看到错误**：
- 复制完整的错误信息
- 根据错误类型查找解决方案

---

## 🔧 常见修复方案

### 修复 1: 更新 requirements.txt

如果缺少依赖：
```bash
cd ~/Desktop/linkedin_recruiter
echo "missing-package>=1.0.0" >> requirements.txt
git add requirements.txt
git commit -m "添加缺失的依赖"
git push origin main
```

Render 会自动重新部署。

### 修复 2: 修改 web_server.py

如果端口配置有问题：
```python
# 确保这段代码在 web_server.py 的最后
if __name__ == '__main__':
    PORT = int(os.getenv('PORT', 3000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(debug=DEBUG, host='0.0.0.0', port=PORT)
```

### 修复 3: 检查 Procfile

确保 Procfile 内容正确：
```
web: python web_server.py
```

注意：
- 没有多余的空格
- 使用 `web:` 而不是 `Web:` 或 `WEB:`
- 文件名是 `Procfile` 不是 `Procfile.txt`

---

## ✅ 验证部署成功

### 1. 检查服务状态
- Render Dashboard 显示绿色 "Live"
- 没有错误日志

### 2. 访问服务
```bash
# 获取你的 Render URL（类似）
https://linkedin-recruiter-xxxx.onrender.com
```

### 3. 测试功能
- [ ] 首页加载正常
- [ ] 可以输入搜索条件
- [ ] 点击搜索后有响应
- [ ] 实时日志显示

---

## 🆘 需要帮助？

如果按照以上步骤仍然无法部署，请提供：

1. **Render 日志截图**（完整的错误信息）
2. **服务配置截图**（Build Command、Start Command）
3. **环境变量列表**（隐藏敏感值）

我会根据具体错误信息提供针对性的解决方案。

---

## 📚 相关资源

- [Render 官方文档](https://render.com/docs)
- [Python 部署指南](https://render.com/docs/deploy-flask)
- [项目部署检查清单](DEPLOYMENT_CHECKLIST.md)
