# LinkedIn 招聘系统部署指南

## 🚀 部署选项

### 选项 1：Railway（推荐，最简单）

1. **准备工作**
   - 注册 [Railway](https://railway.app/) 账号
   - 连接 GitHub 账号

2. **部署步骤**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择你的仓库
   - Railway 会自动检测并部署

3. **环境变量配置**
   在 Railway 项目设置中添加：
   - `PORT=3000`
   - 其他 API Keys（如果需要）

4. **访问**
   - Railway 会自动分配一个公共 URL
   - 例如：`https://your-app.railway.app`

### 选项 2：Render

1. **注册** [Render](https://render.com/)
2. **创建 Web Service**
   - 连接 GitHub 仓库
   - 选择 Python 环境
   - 构建命令：`pip install -r requirements.txt`
   - 启动命令：`python web_server.py`

### 选项 3：Heroku

1. **安装 Heroku CLI**
   ```bash
   brew install heroku/brew/heroku
   ```

2. **登录并创建应用**
   ```bash
   heroku login
   heroku create your-app-name
   ```

3. **部署**
   ```bash
   git push heroku main
   ```

## 📋 部署前检查清单

- [ ] 已创建 `requirements.txt`
- [ ] 已创建 `Procfile`
- [ ] 已创建 `runtime.txt`
- [ ] 已配置环境变量
- [ ] 已测试本地运行
- [ ] 已准备 OAuth 凭证

## ⚠️ 重要注意事项

### 1. OAuth 凭证

公共部署时，OAuth 认证会有问题，因为：
- 每个用户需要自己的 Google 账号授权
- 不能共享 `token.pickle`

**解决方案**：
- 使用服务账号（Service Account）
- 或者让每个用户自己配置 OAuth

### 2. API Keys

不要在代码中硬编码 API Keys，使用环境变量：
```python
import os
SERPER_KEY = os.getenv('SERPER_API_KEY')
```

### 3. 数据库

如果需要保存用户数据，考虑添加数据库：
- PostgreSQL（Railway/Render 免费提供）
- MongoDB Atlas（免费层）

## 🔒 安全建议

1. **添加用户认证**
   - 使用 Flask-Login
   - 或者简单的密码保护

2. **限制请求频率**
   - 使用 Flask-Limiter
   - 防止滥用

3. **HTTPS**
   - Railway/Render 自动提供
   - 确保所有通信加密

## 📊 监控和日志

- Railway：内置日志查看
- Render：实时日志
- 考虑添加 Sentry 进行错误追踪

## 💰 成本估算

- **Railway**：免费层 $5/月额度
- **Render**：免费层（有限制）
- **Heroku**：免费层已取消，最低 $7/月

## 🎯 推荐方案

对于你的项目，我推荐：
1. **Railway**（最简单，自动部署）
2. 添加简单的密码保护
3. 使用环境变量管理敏感信息

需要我帮你创建部署配置文件吗？
