# 🚀 快速部署到 Railway

## 步骤 1：准备 GitHub 仓库

1. **创建 GitHub 仓库**
   ```bash
   cd ~/Desktop
   git init
   git add .
   git commit -m "Initial commit: LinkedIn Recruiter System"
   ```

2. **推送到 GitHub**
   ```bash
   # 在 GitHub 创建新仓库后
   git remote add origin https://github.com/YOUR_USERNAME/linkedin-recruiter.git
   git branch -M main
   git push -u origin main
   ```

## 步骤 2：部署到 Railway

1. **访问** [Railway.app](https://railway.app/)
2. **登录** 使用 GitHub 账号
3. **点击** "New Project"
4. **选择** "Deploy from GitHub repo"
5. **选择** 你的 `linkedin-recruiter` 仓库
6. **等待** 自动部署完成

## 步骤 3：配置环境变量

在 Railway 项目设置中添加：

```
PORT=3000
DEBUG=False
SERPER_API_KEY=你的Serper密钥
```

## 步骤 4：获取公共 URL

1. Railway 会自动分配一个 URL
2. 点击 "Settings" → "Generate Domain"
3. 你会得到类似：`https://your-app.up.railway.app`

## 🎉 完成！

现在任何人都可以访问你的招聘系统了！

## ⚠️ 重要提醒

### OAuth 问题

公共部署时，Google OAuth 会有问题，因为：
- `token.pickle` 是个人凭证，不能共享
- 每个用户需要自己授权

**临时解决方案**：
- 移除 Google Sheets 导出功能
- 或者只导出 JSON/Markdown 文件

### API Keys 安全

不要在代码中硬编码 API Keys！使用环境变量：
```python
import os
SERPER_KEY = os.getenv('SERPER_API_KEY', 'default_key')
```

## 📊 监控

- Railway 提供实时日志
- 可以在 Dashboard 查看应用状态
- 自动重启失败的服务

## 💰 费用

- Railway 免费层：$5/月额度
- 足够小规模使用
- 超出后按使用量计费

## 🔒 添加密码保护（可选）

如果想限制访问，可以添加简单的密码保护。需要我帮你实现吗？
