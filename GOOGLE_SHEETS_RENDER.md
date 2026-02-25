# Google Sheets 导出在 Render 上的配置

## 问题说明

Google Sheets 导出功能需要 OAuth 认证文件：
- `oauth_credentials.json` - OAuth 客户端凭证
- `token.pickle` - 用户授权令牌

这些文件在本地存在，但因为安全原因被 `.gitignore` 排除，没有上传到 GitHub/Render。

## 解决方案

### 方案 1: 使用 Render Secret Files（推荐）

1. **准备文件内容**
   ```bash
   cd ~/Desktop/linkedin_recruiter
   cat oauth_credentials.json
   cat token.pickle | base64
   ```

2. **在 Render Dashboard 添加 Secret Files**
   - 进入你的服务页面
   - 点击 "Environment" 标签
   - 滚动到 "Secret Files" 部分
   - 点击 "Add Secret File"
   
   **添加 oauth_credentials.json:**
   - Filename: `oauth_credentials.json`
   - Contents: 粘贴 `oauth_credentials.json` 的完整内容
   
   **添加 token.pickle:**
   - Filename: `token.pickle`
   - Contents: 粘贴 base64 编码的内容
   - 注意：需要在代码中解码

3. **保存并重新部署**

### 方案 2: 禁用 Google Sheets 导出（临时方案）

如果暂时不需要 Google Sheets 导出功能，可以修改代码跳过这部分。

让我创建一个不依赖 Google Sheets 的版本：

