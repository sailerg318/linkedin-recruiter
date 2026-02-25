# Google Sheets 无法创建 - 故障排查指南

## 问题：添加了环境变量但还是没有创建 Google Sheets

### 快速检查清单

1. **确认环境变量已添加**
   - 在 Render Dashboard → 你的服务 → Environment
   - 检查是否有 `GOOGLE_TOKEN_BASE64` 变量
   - 值应该是一长串 Base64 编码（约 1000+ 字符）

2. **确认已重新部署**
   - 添加环境变量后，Render 应该自动触发重新部署
   - 查看部署状态是否为 "Live"（绿色）

3. **查看网页日志**
   - 在网页中执行搜索
   - 查看实时日志输出
   - 应该看到 "步骤 2: 初始化 Google Sheets"

---

## 常见问题和解决方案

### 问题 1: 环境变量值不正确

**症状**：日志显示 "Base64 解码失败" 或 "Token 反序列化失败"

**解决方案**：
1. 确认复制的 Base64 字符串完整（没有截断）
2. 确认没有多余的空格或换行符
3. 重新生成 Base64：
   ```bash
   cd ~/Desktop/linkedin_recruiter
   base64 -i token.pickle
   ```
4. 复制完整输出，重新设置环境变量

### 问题 2: Token 已过期

**症状**：日志显示 "Token 无效" 或 "Token 过期"

**解决方案**：
1. 在本地重新认证：
   ```bash
   cd ~/Desktop/linkedin_recruiter
   python google_sheets_exporter.py
   ```
2. 重新生成 Base64：
   ```bash
   base64 -i token.pickle
   ```
3. 更新 Render 环境变量

### 问题 3: 缺少 OAuth 凭证文件

**症状**：日志显示 "未找到 oauth_credentials.json"

**解决方案**：
这个文件不需要上传到 Render，token.pickle 中已包含所有必要信息。
如果仍然报错，检查 `google_sheets_exporter.py` 是否正确处理环境变量。

### 问题 4: API 权限不足

**症状**：日志显示 "Permission denied" 或 "Insufficient permissions"

**解决方案**：
1. 确认 OAuth 应用有以下权限：
   - `https://www.googleapis.com/auth/spreadsheets`
   - `https://www.googleapis.com/auth/drive.file`
2. 在 Google Cloud Console 重新授权

### 问题 5: 网络连接问题

**症状**：日志显示 "Connection timeout" 或 "Network error"

**解决方案**：
1. Render 服务器可能无法访问 Google API
2. 检查 Render 服务状态
3. 稍后重试

---

## 诊断步骤

### 步骤 1: 运行诊断脚本（在 Render Shell 中）

```bash
python diagnose_google_sheets.py
```

这会检查：
- ✅ 环境变量是否设置
- ✅ Base64 解码是否成功
- ✅ Token 是否有效
- ✅ Google Sheets 连接是否正常
- ✅ 是否能创建测试表格

### 步骤 2: 查看详细日志

在网页中执行搜索，查看日志输出：

**正常情况**：
```
步骤 2: 初始化 Google Sheets
======================================================================
从环境变量读取 OAuth token...
✓ Token 加载成功
✓ Google Sheets 客户端创建成功
  ✓ 已设置为所有人可见（只读）
  ✓ Google Sheets 创建成功
  链接: https://docs.google.com/spreadsheets/d/...
```

**异常情况**：
```
步骤 2: 初始化 Google Sheets
======================================================================
⚠️  未找到 oauth_credentials.json，Google Sheets 导出功能已禁用
```
或
```
❌ Google Sheets 初始化异常: ...
```

### 步骤 3: 检查环境变量格式

正确的 `GOOGLE_TOKEN_BASE64` 应该：
- 长度约 1000-1500 字符
- 只包含 Base64 字符（A-Z, a-z, 0-9, +, /, =）
- 没有空格或换行符

**示例**（前 100 字符）：
```
gASVXAQAAAAAAACMGWdvb2dsZS5vYXV0aDIuY3JlZGVudGlhbHOUjAtDcmVkZW50aWFsc5STlCmBlH2UKIwFdG9rZW6U...
```

---

## 手动测试

### 在本地测试

```bash
cd ~/Desktop/linkedin_recruiter

# 设置环境变量
export GOOGLE_TOKEN_BASE64="$(base64 -i token.pickle)"

# 运行诊断
python diagnose_google_sheets.py

# 测试完整流程
python web_server.py
```

访问 http://localhost:3000，执行搜索，查看是否能创建 Google Sheets。

---

## 如果所有方法都失败

### 临时方案：使用本地 OAuth 文件

1. 将 `oauth_credentials.json` 和 `token.pickle` 上传到 Render
2. 使用 Render 的 Persistent Disk 功能
3. 修改代码读取文件而不是环境变量

### 长期方案：使用 Service Account

1. 在 Google Cloud Console 创建 Service Account
2. 下载 JSON 密钥文件
3. 修改代码使用 Service Account 认证
4. 不需要 OAuth 流程

---

## 联系支持

如果问题仍然存在，请提供：
1. Render 服务 URL
2. 网页日志截图（执行搜索后的完整日志）
3. 环境变量列表（隐藏敏感值）
4. `diagnose_google_sheets.py` 的输出

我会根据具体错误信息提供针对性的解决方案。
