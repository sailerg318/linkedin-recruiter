# LinkedIn 招聘系统 - 部署配置检查清单

## ✅ 已完成的配置

### 1. 核心部署文件
- ✅ [`Procfile`](Procfile:1) - Render/Heroku 启动配置
  ```
  web: python web_server.py
  ```

- ✅ [`runtime.txt`](runtime.txt:1) - Python 版本指定
  ```
  python-3.13.0
  ```

- ✅ [`requirements.txt`](requirements.txt:1) - 依赖包列表
  - Flask 3.0+
  - Flask-CORS 4.0+
  - requests
  - gspread (Google Sheets)
  - google-auth 相关包

### 2. Web 服务配置
- ✅ [`web_server.py`](web_server.py:159) - 端口配置
  - 支持环境变量 `PORT`（生产环境）
  - 默认端口 3000（本地开发）
  - 监听 `0.0.0.0`（允许外部访问）

- ✅ [`web_interface.html`](web_interface.html:362) - API 地址自动检测
  ```javascript
  const API_BASE = window.location.hostname === 'localhost'
      ? 'http://localhost:3000/api'
      : '/api';
  ```

### 3. 环境变量配置
- ✅ [`.env.example`](.env.example:1) - 环境变量模板
  - `SERPER_API_KEY` - Serper 搜索 API（必需）
  - `GEMINI_API_KEY` - Gemini AI API（必需）
  - `PORT` - Web 服务端口（可选，默认 3000）
  - `DEBUG` - 调试模式（可选，默认 True）

### 4. 安全配置
- ✅ [`.gitignore`](.gitignore:1) - 敏感文件排除
  - `.env` - 环境变量文件
  - `token.pickle` - OAuth token
  - `oauth_credentials.json` - OAuth 凭证
  - `config_local.py` - 本地配置

## 📋 部署前检查清单

### Render 部署配置
1. **创建 Web Service**
   - Repository: `https://github.com/sailerg318/linkedin-recruiter`
   - Branch: `main`
   - Root Directory: 留空或 `linkedin_recruiter`

2. **Build & Start 命令**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python web_server.py`

3. **环境变量设置**（在 Render Dashboard 中配置）
   ```
   SERPER_API_KEY=你的_serper_api_key
   GEMINI_API_KEY=你的_gemini_api_key
   PORT=10000  # Render 会自动设置
   DEBUG=False
   ```

4. **实例类型**
   - Free（免费版）
   - 注意：15 分钟无活动后会休眠

### 本地测试
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入真实的 API keys

# 3. 启动服务
python web_server.py

# 4. 访问
open http://localhost:3000
```

## ⚠️ 注意事项

### 1. API Keys 管理
- ❌ **不要**将真实的 API keys 提交到 Git
- ✅ 使用环境变量或 Render 的 Secret Files
- ✅ 在生产环境中设置环境变量

### 2. OAuth 配置（Google Sheets）
- `oauth_credentials.json` - 需要手动上传到 Render
- `token.pickle` - 首次运行时生成，需要持久化存储
- 建议使用 Render 的 Persistent Disk 或外部存储

### 3. 性能优化
- Render 免费版限制：
  - 512 MB RAM
  - 0.1 CPU
  - 15 分钟无活动休眠
- 建议：
  - 使用缓存减少 API 调用
  - 优化搜索批次大小
  - 考虑升级到付费版

### 4. 日志监控
- Render 提供实时日志查看
- [`task_logger.py`](task_logger.py:1) 实现了日志捕获
- 前端实时显示搜索进度

## 🚀 部署流程

### 方式 1: Render（推荐）
1. 推送代码到 GitHub
2. 在 Render 创建 Web Service
3. 连接 GitHub 仓库
4. 配置环境变量
5. 点击 Deploy

### 方式 2: Heroku
```bash
# 1. 登录 Heroku
heroku login

# 2. 创建应用
heroku create linkedin-recruiter-app

# 3. 设置环境变量
heroku config:set SERPER_API_KEY=your_key
heroku config:set GEMINI_API_KEY=your_key

# 4. 部署
git push heroku main

# 5. 打开应用
heroku open
```

### 方式 3: Docker（高级）
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "web_server.py"]
```

## 📊 部署后验证

### 1. 健康检查
- 访问首页：`https://your-app.onrender.com/`
- 检查 API：`https://your-app.onrender.com/api/config`

### 2. 功能测试
- [ ] 前端页面正常加载
- [ ] 搜索功能可用
- [ ] 实时日志显示
- [ ] 结果导出（如果配置了 Google Sheets）

### 3. 性能监控
- 响应时间 < 3 秒
- API 调用成功率 > 95%
- 内存使用 < 400 MB

## 🔧 故障排查

### 问题 1: 应用无法启动
- 检查 Render 日志
- 验证 `requirements.txt` 依赖
- 确认 Python 版本匹配

### 问题 2: API 调用失败
- 检查环境变量是否正确设置
- 验证 API keys 有效性
- 查看 API 配额限制

### 问题 3: 前端无法连接后端
- 检查 CORS 配置
- 验证 API 路径（`/api`）
- 查看浏览器控制台错误

## 📚 相关文档
- [项目总结](PROJECT_SUMMARY.md)
- [快速部署指南](QUICK_DEPLOY.md)
- [Web 使用指南](WEB_GUIDE.md)
- [故障排查](TROUBLESHOOTING.md)

## 🎯 下一步
1. 获取 Render 部署 URL
2. 配置自定义域名（可选）
3. 设置监控告警
4. 优化性能和成本
