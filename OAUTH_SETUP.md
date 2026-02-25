# Google OAuth 设置指南

## 为什么使用 OAuth？

- ✅ 使用您自己的 Google 账号（2TB 存储空间）
- ✅ 不受服务账号 15GB 限制
- ✅ 文件直接保存在您的 Drive 中
- ✅ 更简单的权限管理

## 设置步骤

### 1. 创建 Google Cloud 项目

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 记下项目 ID

### 2. 启用 API

1. 在左侧菜单选择 **API 和服务** > **启用的 API 和服务**
2. 点击 **+ 启用 API 和服务**
3. 搜索并启用以下 API：
   - **Google Sheets API**
   - **Google Drive API**

### 3. 创建 OAuth 客户端凭证

1. 在左侧菜单选择 **API 和服务** > **凭据**
2. 点击 **+ 创建凭据** > **OAuth 客户端 ID**
3. 如果提示配置同意屏幕：
   - 选择 **外部**（如果是个人账号）
   - 填写应用名称（如 "LinkedIn Recruiter"）
   - 添加您的邮箱
   - 保存并继续
4. 应用类型选择 **桌面应用**
5. 名称填写 "LinkedIn Recruiter Desktop"
6. 点击 **创建**

### 4. 下载凭证文件

1. 在凭据列表中找到刚创建的 OAuth 客户端
2. 点击右侧的下载图标（⬇️）
3. 将下载的 JSON 文件重命名为 `oauth_credentials.json`
4. 将文件放到 `linkedin_recruiter` 目录下

### 5. 安装依赖

```bash
cd ~/Desktop/linkedin_recruiter
pip3 install google-auth-oauthlib
```

### 6. 首次认证

运行测试脚本：

```bash
python3 test_oauth.py
```

- 浏览器会自动打开
- 登录您的 Google 账号
- 点击 **允许** 授权应用访问
- 认证成功后，凭证会保存在 `token.pickle` 文件中
- 下次使用时不需要重新认证

## 文件说明

- `oauth_credentials.json` - OAuth 客户端凭证（从 Google Cloud Console 下载）
- `token.pickle` - 访问令牌（首次认证后自动生成，不要删除）

## 安全提示

⚠️ **不要将这些文件提交到 Git**

已在 `.gitignore` 中添加：
```
oauth_credentials.json
token.pickle
```

## 使用示例

```python
from google_sheets_exporter_oauth import GoogleSheetsExporterOAuth

# 创建导出器
exporter = GoogleSheetsExporterOAuth("oauth_credentials.json")

# 导出候选人
url = exporter.export_candidates(
    candidates=candidates,
    requirement_text="岗位要求",
    job_title="OD Manager",
    share_emails=["colleague@example.com"]  # 可选：分享给其他人
)

print(f"表格链接: {url}")
```

## 常见问题

### Q: 认证后浏览器显示 "localhost refused to connect"？
A: 这是正常的，认证已经完成。关闭浏览器窗口即可。

### Q: 如何重新认证？
A: 删除 `token.pickle` 文件，然后重新运行脚本。

### Q: 可以在服务器上使用吗？
A: OAuth 需要浏览器交互，不适合服务器。服务器环境请使用服务账号方式。

### Q: 凭证会过期吗？
A: 访问令牌会过期，但会自动刷新。只要 `token.pickle` 存在就不需要重新认证。

## 对比：OAuth vs 服务账号

| 特性 | OAuth | 服务账号 |
|------|-------|---------|
| 存储空间 | 用户账号空间（2TB） | 15GB |
| 认证方式 | 浏览器授权 | JSON 密钥文件 |
| 文件所有者 | 用户自己 | 服务账号 |
| 适用场景 | 个人使用 | 自动化/服务器 |
| 设置难度 | 简单 | 中等 |

## 推荐方案

- ✅ **个人使用**: 使用 OAuth（本方案）
- ✅ **自动化/服务器**: 使用服务账号
