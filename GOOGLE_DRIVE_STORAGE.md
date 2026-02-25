# Google Drive 服务账号存储空间管理

## 问题说明

服务账号有独立的 Google Drive 存储空间（默认 15GB 免费），与你个人账号的空间是分开的。

当看到错误 `The user's Drive storage quota has been exceeded.` 时，说明服务账号的 15GB 空间已满。

## 解决方案

### 方案 1: 查看和清理服务账号的 Drive 空间

#### 步骤 1: 获取服务账号邮箱

打开你的 `google_credentials.json` 文件，查找 `client_email` 字段：

```json
{
  "type": "service_account",
  "project_id": "your-project",
  "private_key_id": "...",
  "private_key": "...",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  ...
}
```

复制这个邮箱地址。

#### 步骤 2: 使用服务账号登录 Google Drive

**注意**: 服务账号不能直接登录 Google Drive 网页版。

你需要通过以下方式查看服务账号创建的文件：

**方法 A: 在你的个人 Drive 中查看共享文件**

1. 访问 https://drive.google.com
2. 点击左侧 "与我共享"
3. 查找由服务账号创建的文件
4. 删除不需要的文件

**方法 B: 使用 Google Cloud Console**

1. 访问 https://console.cloud.google.com
2. 选择你的项目
3. 导航到 "IAM & Admin" > "Service Accounts"
4. 找到你的服务账号
5. 点击 "Keys" 标签
6. 查看该服务账号的使用情况

**方法 C: 使用代码查看和删除文件**

创建一个脚本来列出和删除服务账号的文件：

```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

# 初始化
credentials = service_account.Credentials.from_service_account_file(
    'google_credentials.json',
    scopes=['https://www.googleapis.com/auth/drive']
)

service = build('drive', 'v3', credentials=credentials)

# 列出所有文件
results = service.files().list(
    pageSize=100,
    fields="files(id, name, size, createdTime)"
).execute()

files = results.get('files', [])

print(f"找到 {len(files)} 个文件:")
for file in files:
    size_mb = int(file.get('size', 0)) / (1024 * 1024)
    print(f"- {file['name']} ({size_mb:.2f} MB)")
    print(f"  ID: {file['id']}")
    print(f"  创建时间: {file['createdTime']}")
    
    # 删除文件（取消注释以执行）
    # service.files().delete(fileId=file['id']).execute()
    # print(f"  已删除")
```

### 方案 2: 创建新的服务账号

如果旧的服务账号空间已满且无法清理，创建一个新的：

1. 访问 https://console.cloud.google.com
2. 选择你的项目
3. 导航到 "IAM & Admin" > "Service Accounts"
4. 点击 "Create Service Account"
5. 填写信息并创建
6. 创建新的 Key（JSON 格式）
7. 下载并替换 `google_credentials.json`

### 方案 3: 使用 Google Workspace 账号

如果你有 Google Workspace 账号（企业版），服务账号可以使用组织的存储空间，而不是 15GB 限制。

### 方案 4: 定期清理（推荐）

在代码中添加自动清理逻辑，定期删除旧的表格：

```python
def cleanup_old_sheets(days=30):
    """删除超过指定天数的表格"""
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    results = service.files().list(
        q=f"mimeType='application/vnd.google-apps.spreadsheet' and createdTime < '{cutoff_date.isoformat()}Z'",
        fields="files(id, name, createdTime)"
    ).execute()
    
    files = results.get('files', [])
    
    for file in files:
        service.files().delete(fileId=file['id']).execute()
        print(f"已删除: {file['name']}")
```

## 当前推荐方案

由于服务账号的存储限制，我建议：

### 临时解决方案

使用 Markdown 或 JSON 导出，然后手动上传到你的个人 Google Drive：

```python
from recruiter_pro import LinkedInRecruiterPro

recruiter = LinkedInRecruiterPro()

# 导出为 Markdown
recruiter.export_to_markdown(candidates, "results.md")

# 或导出为 JSON
recruiter.export_to_json(candidates, "results.json")
```

然后：
1. 打开 https://drive.google.com
2. 上传文件
3. 右键 -> 打开方式 -> Google Sheets（如果是 CSV）

### 长期解决方案

1. **定期清理**: 每周删除旧的测试表格
2. **使用新服务账号**: 每个项目使用独立的服务账号
3. **升级到 Workspace**: 如果需要大量存储空间

## 检查服务账号存储使用情况

运行以下脚本查看服务账号的文件：

```bash
cd linkedin_recruiter
python3 -c "
from google.oauth2 import service_account
from googleapiclient.discovery import build

credentials = service_account.Credentials.from_service_account_file(
    'google_credentials.json',
    scopes=['https://www.googleapis.com/auth/drive']
)

service = build('drive', 'v3', credentials=credentials)

results = service.files().list(
    pageSize=100,
    fields='files(id, name, size, createdTime)'
).execute()

files = results.get('files', [])
total_size = sum(int(f.get('size', 0)) for f in files)

print(f'文件数量: {len(files)}')
print(f'总大小: {total_size / (1024*1024):.2f} MB')
print(f'剩余空间: {15*1024 - total_size/(1024*1024):.2f} MB')
"
```

## 总结

服务账号的 15GB 存储限制是 Google 的默认设置。最简单的解决方案是：

1. **短期**: 使用 Markdown/JSON 导出，手动上传到你的个人 Drive
2. **长期**: 定期清理服务账号的旧文件，或创建新的服务账号
