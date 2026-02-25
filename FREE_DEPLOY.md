# 🆓 完全免费的部署方案

## 方案 1：Render（推荐，完全免费）

### 优点
- ✅ 完全免费（有限制但够用）
- ✅ 自动 HTTPS
- ✅ 自动部署
- ✅ 支持 Python

### 限制
- ⚠️ 15 分钟无活动会休眠
- ⚠️ 每月 750 小时免费（够用）
- ⚠️ 启动可能需要 30 秒

### 部署步骤

1. **注册** [Render.com](https://render.com/)

2. **创建 Web Service**
   - 点击 "New +" → "Web Service"
   - 连接 GitHub 仓库
   - 配置：
     - Name: `linkedin-recruiter`
     - Environment: `Python 3`
     - Build Command: `pip install -r linkedin_recruiter/requirements.txt`
     - Start Command: `python linkedin_recruiter/web_server.py`
     - Instance Type: **Free**

3. **环境变量**
   - 添加 `PORT=10000`（Render 默认）
   - 添加 `DEBUG=False`

4. **完成！**
   - 获得免费 URL：`https://your-app.onrender.com`

---

## 方案 2：Vercel（免费，但需要改造）

### 优点
- ✅ 完全免费
- ✅ 全球 CDN
- ✅ 不会休眠

### 缺点
- ⚠️ 需要改造成 Serverless 函数
- ⚠️ 不支持长时间运行的任务

### 适用场景
- 轻量级搜索
- 快速查询

---

## 方案 3：PythonAnywhere（免费层）

### 优点
- ✅ 完全免费
- ✅ 专为 Python 设计
- ✅ 不会休眠

### 限制
- ⚠️ CPU 时间有限
- ⚠️ 每天重启一次
- ⚠️ 只能访问白名单 API

### 部署步骤

1. **注册** [PythonAnywhere.com](https://www.pythonanywhere.com/)

2. **上传代码**
   - 使用 Git 克隆仓库
   - 或者手动上传文件

3. **配置 Web App**
   - 创建新的 Web App
   - 选择 Flask
   - 配置 WSGI 文件

---

## 方案 4：Glitch（免费，简单）

### 优点
- ✅ 完全免费
- ✅ 在线编辑器
- ✅ 自动部署

### 限制
- ⚠️ 5 分钟无活动会休眠
- ⚠️ 项目大小限制

### 部署步骤

1. **访问** [Glitch.com](https://glitch.com/)
2. **导入** GitHub 仓库
3. **自动运行**

---

## 🏆 最佳推荐：Render

**为什么选 Render？**
1. 完全免费
2. 部署最简单
3. 功能最完整
4. 支持 Python 完美

**唯一缺点：**
- 15 分钟无活动会休眠
- 首次访问需要等待 30 秒唤醒

**解决方案：**
- 使用 UptimeRobot 每 14 分钟 ping 一次（免费）
- 保持应用始终活跃

---

## 📋 Render 详细部署指南

### 1. 准备工作

确保项目根目录有：
- `Procfile`（已创建 ✅）
- `runtime.txt`（已创建 ✅）
- `linkedin_recruiter/requirements.txt`（已存在 ✅）

### 2. 推送到 GitHub

```bash
cd ~/Desktop
git init
git add .
git commit -m "Deploy to Render"
git remote add origin https://github.com/YOUR_USERNAME/linkedin-recruiter.git
git push -u origin main
```

### 3. 在 Render 部署

1. 访问 https://render.com/
2. 点击 "Get Started for Free"
3. 用 GitHub 登录
4. 点击 "New +" → "Web Service"
5. 选择你的仓库
6. 填写配置：
   - **Name**: `linkedin-recruiter`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r linkedin_recruiter/requirements.txt`
   - **Start Command**: `python linkedin_recruiter/web_server.py`
   - **Instance Type**: 选择 **Free**
7. 点击 "Create Web Service"

### 4. 配置环境变量

在 Render Dashboard：
1. 点击 "Environment"
2. 添加变量：
   - `PORT=10000`
   - `DEBUG=False`
   - `SERPER_API_KEY=你的密钥`（如果需要）

### 5. 等待部署

- 首次部署需要 5-10 分钟
- 完成后会显示 URL
- 例如：`https://linkedin-recruiter.onrender.com`

---

## 🎯 保持应用活跃（可选）

使用 [UptimeRobot](https://uptimerobot.com/)（免费）：

1. 注册 UptimeRobot
2. 添加新监控
3. URL: 你的 Render URL
4. 监控间隔: 5 分钟
5. 完成！应用不会休眠

---

## 💡 总结

| 平台 | 费用 | 休眠 | 推荐度 |
|------|------|------|--------|
| **Render** | 免费 | 15分钟 | ⭐⭐⭐⭐⭐ |
| PythonAnywhere | 免费 | 不休眠 | ⭐⭐⭐ |
| Glitch | 免费 | 5分钟 | ⭐⭐ |
| Vercel | 免费 | 不休眠 | ⭐（需改造）|

**最终推荐：Render + UptimeRobot = 完美免费方案！**
