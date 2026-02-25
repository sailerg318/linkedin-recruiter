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

### Google Sheets 导出（必需，用于导出结果）

```
GOOGLE_TOKEN_BASE64=gASVXAQAAAAAAACMGWdvb2dsZS5vYXV0aDIuY3JlZGVudGlhbHOUjAtDcmVkZW50aWFsc5STlCmBlH2UKIwFdG9rZW6UjP15YTI5LmEwQVRrb0NjNTFYdF85MzU4NHkxRDhWdmpMQ1dRUGxzT1hpU1MzR2JIYVZsZUlLWXlqbncxWHVkSGRJWGdEeFBkbDNCbEwwQ0lUT0dxUm9nRlRHM0FJMHZpeS1qYk5aSkN4Vjc5dDlOMXJORElvUjJBZ1JUQ2lhSWRlUnQ4dkxLbDlZTjVHd3ZIekQ0Ykk4Y1EzVDQ3MEhYbGRUQTZnYjZ5Wk9YS29DQ3JEdUpmMHY3RGJTUDNSMXloZFlDSkRiMmlzYW1YcFpMNGFDZ1lLQWIwU0FSY1NGUUhHWDJNaUx5RU5XN3ZVX21yZEZ6MnVxQ2E1dGcwMjA2lIwGZXhwaXJ5lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+oCGQQrCQAAAJSFlFKUjBFfcXVvdGFfcHJvamVjdF9pZJROjA9fdHJ1c3RfYm91bmRhcnmUTowQX3VuaXZlcnNlX2RvbWFpbpSMDmdvb2dsZWFwaXMuY29tlIwZX3VzZV9ub25fYmxvY2tpbmdfcmVmcmVzaJSJjAdfc2NvcGVzlF2UKIwsaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vYXV0aC9zcHJlYWRzaGVldHOUjCpodHRwczovL3d3dy5nb29nbGVhcGlzLmNvbS9hdXRoL2RyaXZlLmZpbGWUZYwPX2RlZmF1bHRfc2NvcGVzlE6MDl9yZWZyZXNoX3Rva2VulIxnMS8vMGdwUFd6SjljdHhQbUNnWUlBUkFBR0JBU053Ri1MOUlyc0NTYzNFSHpuaGh1V3NPWFo1TnZIRXgxZ2NRVlk5cVp4clVOTGVYVk9CWWFzMnI1MEc2LW4yNXJiUmhCX193Z1VzNJSMCV9pZF90b2tlbpROjA9fZ3JhbnRlZF9zY29wZXOUXZQojCpodHRwczovL3d3dy5nb29nbGVhcGlzLmNvbS9hdXRoL2RyaXZlLmZpbGWUjCxodHRwczovL3d3dy5nb29nbGVhcGlzLmNvbS9hdXRoL3NwcmVhZHNoZWV0c5RljApfdG9rZW5fdXJplIwjaHR0cHM6Ly9vYXV0aDIuZ29vZ2xlYXBpcy5jb20vdG9rZW6UjApfY2xpZW50X2lklIxJMTA4NTY2NDE4MDYxNC0xcGV1dWk2ZnRkdHAxN2NncDNhcWg0cDBjODQ3YXNtby5hcHBzLmdvb2dsZXVzZXJjb250ZW50LmNvbZSMDl9jbGllbnRfc2VjcmV0lIwjR09DU1BYLWtjRURTT1gtNmR2eER1TWtUeHYxX2tiOUVXdkyUjAtfcmFwdF90b2tlbpROjBZfZW5hYmxlX3JlYXV0aF9yZWZyZXNolImMCF9hY2NvdW50lIwAlIwPX2NyZWRfZmlsZV9wYXRolE51Yi4=
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
