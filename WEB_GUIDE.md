# LinkedIn 招聘系统 - Web 界面使用指南

## 🚀 快速启动

### 1. 启动 Web 服务器

在终端中运行：

```bash
cd ~/Desktop/linkedin_recruiter
python3 web_server.py
```

服务器将在 **http://localhost:8080** 启动

### 2. 访问 Web 界面

在浏览器中打开：**http://localhost:8080**

## 📋 功能说明

### 主要功能

1. **输入招聘需求**
   - 在文本框中输入岗位要求
   - 例如："我想找 Base 上海的产品经理，5-8年经验，有大厂背景"

2. **配置搜索参数**
   - **搜索引擎**：选择 Serper（推荐）、Gemini 或 Tavily
   - **搜索批次**：每批搜索的候选人数量（默认 50）
   - **Flash 阈值**：粗筛分数线（默认 50）
   - **Pro 阈值**：精筛分数线（默认 70）
   - **分享邮箱**：可选，填写后会自动分享 Google Sheets

3. **查看实时进度**
   - 搜索进度条
   - 实时日志输出
   - 统计数据（搜索数、通过数等）

4. **获取结果**
   - 自动导出到 Google Sheets
   - 点击链接直接查看表格

## 🔍 翻页功能

搜索过程中会自动翻页获取更多结果：

```
============================================================
🔍 Serper 搜索 - 翻页模式
============================================================
目标结果数: 50
预计翻页数: 5
============================================================

📄 正在请求第 1 页 (start=0)...
✓ 第 1 页: 找到 10 位候选人 (去重后 10 位) | 累计: 10 位
📄 正在请求第 2 页 (start=10)...
✓ 第 2 页: 找到 10 位候选人 (去重后 6 位) | 累计: 16 位
...
```

## ✅ 已配置功能

- ✅ OAuth 认证已完成
- ✅ Google Sheets 导出正常
- ✅ Serper 翻页功能已增强
- ✅ 自动去重候选人

## 🛠️ 技术栈

- **后端**：Flask + Python
- **前端**：HTML + CSS + JavaScript
- **搜索**：Serper API（支持翻页）
- **导出**：Google Sheets API（OAuth）

## 📝 注意事项

1. **首次使用**
   - 确保已完成 OAuth 认证（已完成 ✅）
   - 确保 `token.pickle` 文件存在

2. **端口占用**
   - 如果 8080 端口被占用，可以修改 `web_server.py` 中的 `PORT` 变量

3. **长时间运行**
   - 搜索和筛选可能需要几分钟
   - 不要关闭浏览器标签页
   - 可以在终端查看详细日志

## 🔧 故障排除

### 问题：服务器无法启动

```bash
# 检查端口是否被占用
lsof -i :8080

# 如果被占用，杀死进程或更改端口
```

### 问题：Google Sheets 导出失败

```bash
# 重新认证
cd ~/Desktop/linkedin_recruiter
rm -f token.pickle
python3 test_oauth.py
```

### 问题：搜索没有结果

- 检查 Serper API Key 是否有效
- 尝试更改搜索引擎（Gemini 或 Tavily）
- 降低 Flash 阈值

## 📞 需要帮助？

如果遇到问题，请查看：
- [`OAUTH_CONFIG_HELP.md`](OAUTH_CONFIG_HELP.md) - OAuth 配置帮助
- [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) - 故障排除指南
- 终端日志输出

## 🎉 开始使用

1. 打开终端
2. 运行 `cd ~/Desktop/linkedin_recruiter && python3 web_server.py`
3. 在浏览器打开 http://localhost:8080
4. 输入招聘需求，点击"开始搜索"
5. 等待处理完成，查看 Google Sheets 结果

祝你招聘顺利！🚀
