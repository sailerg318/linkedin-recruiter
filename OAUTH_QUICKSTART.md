# OAuth 快速开始

## 🎯 为什么选择 OAuth？

服务账号只有 15GB 存储空间已满，使用 OAuth 可以：
- ✅ 使用您自己的 Google 账号（2TB 空间）
- ✅ 文件直接保存在您的 Drive 中
- ✅ 不受服务账号限制

## 📋 快速设置（5分钟）

### 1. 安装依赖

```bash
cd ~/Desktop/linkedin_recruiter
pip3 install google-auth-oauthlib
```

### 2. 获取 OAuth 凭证

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 选择项目或创建新项目
3. 启用 API：
   - 搜索 "Google Sheets API" → 启用
   - 搜索 "Google Drive API" → 启用
4. 创建凭证：
   - 左侧菜单：**API 和服务** > **凭据**
   - 点击 **+ 创建凭据** > **OAuth 客户端 ID**
   - 应用类型：**桌面应用**
   - 下载 JSON 文件
5. 重命名为 `oauth_credentials.json` 并放到项目目录

### 3. 测试

```bash
python3 test_oauth.py
```

- 浏览器会自动打开
- 登录您的 Google 账号
- 点击"允许"授权
- 完成！

## 🚀 使用方法

### 方式1：直接使用 OAuth 导出器

```python
from google_sheets_exporter_oauth import GoogleSheetsExporterOAuth

exporter = GoogleSheetsExporterOAuth("oauth_credentials.json")
url = exporter.export_candidates(
    candidates=candidates,
    requirement_text="岗位要求",
    job_title="职位名称"
)
```

### 方式2：修改现有脚本

将现有脚本中的：
```python
from google_sheets_exporter import GoogleSheetsExporter
exporter = GoogleSheetsExporter("google_credentials.json")
```

改为：
```python
from google_sheets_exporter_oauth import GoogleSheetsExporterOAuth
exporter = GoogleSheetsExporterOAuth("oauth_credentials.json")
```

## 📁 文件说明

- `oauth_credentials.json` - OAuth 客户端凭证（从 Google Cloud 下载）
- `token.pickle` - 访问令牌（首次认证后自动生成）
- 这两个文件已加入 `.gitignore`，不会被提交

## ❓ 常见问题

**Q: 每次都要重新认证吗？**  
A: 不需要。首次认证后会保存 `token.pickle`，下次自动使用。

**Q: 浏览器显示 "localhost refused to connect"？**  
A: 正常现象，认证已完成，关闭浏览器即可。

**Q: 如何重新认证？**  
A: 删除 `token.pickle` 文件，重新运行脚本。

## 📚 详细文档

查看 [`OAUTH_SETUP.md`](OAUTH_SETUP.md) 了解更多细节。

## ✅ 下一步

OAuth 设置完成后，您可以：
1. 运行 `python3 start.py` 使用交互式菜单
2. 使用 `streaming_pipeline.py` 进行流式处理
3. 使用 `recruiter_pro.py` 批量处理职位

所有导出都会使用您自己的 Google Drive 空间！
