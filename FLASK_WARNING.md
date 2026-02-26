# Flask 开发服务器警告 - 说明

## 警告信息
```
WARNING: This is a development server. Do not use it in a production deployment. 
Use a production WSGI server instead.
```

## 这是什么？

这是 Flask 内置开发服务器的标准警告。Flask 的 `app.run()` 方法使用的是单线程、非优化的开发服务器。

## 对 Render 部署的影响

**好消息：对于小规模应用（如我们的招聘系统），这个警告可以忽略。**

原因：
- ✅ Render 免费版本身就有性能限制
- ✅ 我们的应用主要是后台任务处理，不是高并发 Web 服务
- ✅ 搜索任务在后台线程中运行，不会阻塞主线程

## 如果需要生产级部署

### 方案 1: 使用 Gunicorn（推荐）

1. **添加依赖**
   在 `requirements.txt` 中添加：
   ```
   gunicorn>=21.2.0
   ```

2. **修改 Procfile**
   ```
   web: gunicorn web_server:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
   ```

3. **配置说明**
   - `--workers 2`: 2 个工作进程（适合免费版）
   - `--timeout 120`: 120 秒超时（搜索任务可能较长）
   - `--bind 0.0.0.0:$PORT`: 监听所有接口

### 方案 2: 使用 Waitress

1. **添加依赖**
   ```
   waitress>=2.1.2
   ```

2. **修改 web_server.py**
   ```python
   if __name__ == '__main__':
       PORT = int(os.getenv('PORT', 3000))
       
       if os.getenv('PRODUCTION'):
           # 生产环境使用 Waitress
           from waitress import serve
           print(f"Starting production server on port {PORT}")
           serve(app, host='0.0.0.0', port=PORT)
       else:
           # 开发环境使用 Flask
           app.run(debug=True, host='0.0.0.0', port=PORT)
   ```

3. **修改 Procfile**
   ```
   web: python web_server.py
   ```

4. **添加环境变量**
   ```
   PRODUCTION=True
   ```

## 当前配置是否足够？

**是的！** 对于我们的应用场景：
- ✅ 用户数量有限（个人或小团队使用）
- ✅ 主要是后台任务处理
- ✅ 不需要高并发支持
- ✅ Render 免费版本身就有限制

## 何时需要升级？

如果出现以下情况，考虑使用 Gunicorn：
- ⚠️ 多个用户同时使用
- ⚠️ 响应速度变慢
- ⚠️ 出现超时错误
- ⚠️ 需要更好的稳定性

## 总结

**当前配置：可以正常使用，警告可以忽略**

如果需要更好的性能和稳定性，按照上面的方案 1 添加 Gunicorn 即可。
