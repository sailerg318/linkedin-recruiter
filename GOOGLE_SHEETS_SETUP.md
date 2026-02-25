# Google Sheets配置指南

## 📋 配置步骤

### 1. 创建Google Cloud项目

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 记下项目ID

### 2. 启用Google Sheets API

1. 在Google Cloud Console中，进入"API和服务" > "库"
2. 搜索"Google Sheets API"
3. 点击"启用"
4. 同样启用"Google Drive API"

### 3. 创建服务账号

1. 进入"API和服务" > "凭据"
2. 点击"创建凭据" > "服务账号"
3. 填写服务账号名称，如"linkedin-recruiter"
4. 点击"创建并继续"
5. 角色选择"编辑者"
6. 点击"完成"

### 4. 生成密钥文件

1. 在服务账号列表中，点击刚创建的服务账号
2. 进入"密钥"标签
3. 点击"添加密钥" > "创建新密钥"
4. 选择"JSON"格式
5. 下载密钥文件

### 5. 配置密钥文件

1. 将下载的JSON文件重命名为`google_credentials.json`
2. 放到`linkedin_recruiter/`目录下
3. 确保文件在`.gitignore`中（已配置）

### 6. 获取服务账号邮箱

打开`google_credentials.json`，找到`client_email`字段：
```json
{
  "client_email": "linkedin-recruiter@your-project.iam.gserviceaccount.com",
  ...
}
```

这个邮箱将用于分享Google Sheets。

## 🔧 配置文件示例

`google_credentials.json`的结构：
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "linkedin-recruiter@your-project.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

## ✅ 测试配置

运行测试脚本：
```bash
cd linkedin_recruiter
python3 -c "from google_sheets_exporter import GoogleSheetsExporter; e = GoogleSheetsExporter(); print('✓ 配置成功' if e.connect() else '✗ 配置失败')"
```

## 📝 使用示例

```python
from google_sheets_exporter import GoogleSheetsExporter

exporter = GoogleSheetsExporter("google_credentials.json")

# 导出候选人
url = exporter.export_candidates(
    candidates=analyzed_candidates,
    requirement_text="Base伦敦的OD，7-15年经验，甲乙方背景",
    job_title="OD",
    share_emails=["client@example.com"]  # 分享给客户
)

print(f"Google Sheets链接: {url}")
```

## ⚠️ 注意事项

1. **不要提交密钥文件到Git**
   - 已在`.gitignore`中配置
   - 密钥文件包含敏感信息

2. **分享权限**
   - 服务账号创建的表格默认只有服务账号可访问
   - 需要通过`share_emails`参数分享给其他用户

3. **配额限制**
   - Google Sheets API有每日配额限制
   - 免费版：每天500次读取，300次写入
   - 如需更多，考虑升级到付费版

4. **文件大小**
   - 单个表格最多500万个单元格
   - 对于候选人推荐表格，这个限制足够

## 🔗 相关链接

- [Google Sheets API文档](https://developers.google.com/sheets/api)
- [gspread文档](https://docs.gspread.org/)
- [Google Cloud Console](https://console.cloud.google.com/)
