# Google Sheets OAuth 配置指南

## 当前状态

OAuth 凭证文件已存在：`oauth_credentials.json`

## 问题诊断

刚才的认证失败，可能原因：
1. 浏览器没有正确打开授权页面
2. 授权被拒绝
3. OAuth 应用需要配置测试用户

## 解决方案

### 方案 1：手动访问授权链接

1. 复制上面输出的授权链接
2. 在浏览器中打开
3. 登录你的 Google 账号
4. 点击"允许"授权
5. 重新运行 `python3 test_oauth.py`

### 方案 2：配置 OAuth 应用（推荐）

如果你的 OAuth 应用处于"测试"状态，需要添加测试用户：

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 选择项目：`fluent-flame-467410-u8`
3. 左侧菜单：**API 和服务** > **OAuth 同意屏幕**
4. 在"测试用户"部分，点击 **+ ADD USERS**
5. 添加你的 Google 账号邮箱
6. 保存

### 方案 3：发布 OAuth 应用

如果不想限制测试用户：

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 选择项目：`fluent-flame-467410-u8`
3. 左侧菜单：**API 和服务** > **OAuth 同意屏幕**
4. 点击 **PUBLISH APP** 按钮
5. 确认发布

## 验证 API 是否启用

确保以下 API 已启用：

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 选择项目：`fluent-flame-467410-u8`
3. 左侧菜单：**API 和服务** > **已启用的 API 和服务**
4. 确认以下 API 已启用：
   - ✅ Google Sheets API
   - ✅ Google Drive API

如果没有启用，点击 **+ 启用 API 和服务**，搜索并启用它们。

## 重新测试

完成上述配置后，运行：

```bash
cd ~/Desktop/linkedin_recruiter
rm -f token.pickle  # 删除旧的 token
python3 test_oauth.py
```

## 常见错误

### "access_denied"
- 原因：授权被拒绝或测试用户未配置
- 解决：按照方案 2 添加测试用户

### "invalid_grant"
- 原因：Token 已过期
- 解决：删除 `token.pickle` 重新认证

### "redirect_uri_mismatch"
- 原因：重定向 URI 不匹配
- 解决：在 OAuth 客户端配置中添加 `http://localhost`

## 需要帮助？

如果仍然无法配置，请告诉我：
1. 你的 Google 账号邮箱
2. 是否能访问 Google Cloud Console
3. OAuth 应用的当前状态（测试/生产）
