# Render 环境变量配置

## 在 Render Dashboard 中添加以下环境变量：

### 必需的环境变量

```
SERPER_API_KEY=d88085d4543221682eecd92082f27247f71d902f
```

```
GEMINI_API_KEY=sk-4GNtUWRLAgmHzqipMatkx0RDUZMuJ4Egzgp93WDZKcI9Lh0w
```

```
DEBUG=False
```

### 可选的环境变量

```
TAVILY_API_KEY=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
```

---

## 操作步骤

1. **打开 Render Dashboard**
   - 访问 https://dashboard.render.com
   - 找到你的 `linkedin-recruiter` 服务

2. **进入环境变量设置**
   - 点击左侧菜单的 "Environment" 标签
   - 或者点击服务页面的 "Environment" 按钮

3. **添加环境变量**
   - 点击 "Add Environment Variable" 按钮
   - 逐个添加上面的变量：
     * Key: `SERPER_API_KEY`
     * Value: `d88085d4543221682eecd92082f27247f71d902f`
   
   - 再添加：
     * Key: `GEMINI_API_KEY`
     * Value: `sk-4GNtUWRLAgmHzqipMatkx0RDUZMuJ4Egzgp93WDZKcI9Lh0w`
   
   - 再添加：
     * Key: `DEBUG`
     * Value: `False`

4. **保存并重新部署**
   - 点击 "Save Changes" 按钮
   - Render 会自动触发重新部署（约 2-3 分钟）
   - 等待部署完成（状态变为 "Live"）

5. **验证**
   - 访问你的 Render URL
   - 尝试搜索功能
   - 应该能看到搜索结果了

---

## 注意事项

⚠️ **不要设置 PORT 变量** - Render 会自动设置

⚠️ **确保没有多余的空格** - 复制粘贴时注意

⚠️ **区分大小写** - 变量名必须完全一致
