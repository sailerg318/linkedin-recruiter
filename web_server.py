"""
Flask Web API - LinkedIn 招聘系统后端
提供 RESTful API 供前端调用
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from streaming_pipeline import quick_streaming_pipeline
from task_logger import capture_output_to_task
import threading
import uuid
import os

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 存储任务状态
tasks = {}


@app.route('/')
def index():
    """返回前端页面"""
    return send_from_directory('.', 'web_interface.html')


@app.route('/api/search', methods=['POST'])
def start_search():
    """启动搜索任务"""
    data = request.json
    
    # 生成任务 ID
    task_id = str(uuid.uuid4())
    
    # 初始化任务状态
    tasks[task_id] = {
        'status': 'running',
        'progress': 0,
        'stats': {
            'total_searched': 0,
            'flash_passed': 0,
            'pro_passed': 0,
            'exported': 0
        },
        'logs': [],
        'result': None,
        'error': None
    }
    
    # 在后台线程中执行搜索
    thread = threading.Thread(
        target=run_search_task,
        args=(task_id, data)
    )
    thread.start()
    
    return jsonify({
        'task_id': task_id,
        'message': '任务已启动'
    })


@app.route('/api/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """获取任务状态"""
    if task_id not in tasks:
        return jsonify({'error': '任务不存在'}), 404
    
    return jsonify(tasks[task_id])


def run_search_task(task_id, data):
    """执行搜索任务"""
    try:
        # 打印接收到的数据（调试用）
        print(f"\n{'='*70}")
        print("后端接收到的数据:")
        print(f"{'='*70}")
        print(f"完整数据: {data}")
        print(f"需求文本: {data.get('requirement', '')}")
        print(f"{'='*70}\n")
        
        # 更新状态
        tasks[task_id]['logs'].append('开始解析需求...')
        tasks[task_id]['progress'] = 10
        
        # 准备参数
        user_input = data.get('requirement', '')
        engine = data.get('engine', 'serper')
        search_batch_size = data.get('searchBatch', 50)
        flash_threshold = data.get('flashThreshold', 50)
        pro_threshold = data.get('proThreshold', 70)
        share_email = data.get('shareEmail', '')
        share_emails = [share_email] if share_email else None
        
        tasks[task_id]['logs'].append(f'配置: {engine} 引擎, Flash={flash_threshold}, Pro={pro_threshold}')
        tasks[task_id]['progress'] = 20
        
        # 执行搜索 - 捕获所有输出到任务日志
        tasks[task_id]['logs'].append('开始搜索和筛选...')
        tasks[task_id]['logs'].append(f'📊 需求: {user_input}')
        tasks[task_id]['logs'].append(f'🔍 搜索引擎: {engine}')
        tasks[task_id]['logs'].append(f'📦 批次大小: {search_batch_size}')
        tasks[task_id]['progress'] = 30
        
        # 使用日志捕获器，将所有 print 输出捕获到任务日志
        with capture_output_to_task(task_id, tasks):
            result = quick_streaming_pipeline(
                user_input=user_input,
                search_batch_size=search_batch_size,
                screen_batch_size=10,
                flash_threshold=flash_threshold,
                pro_threshold=pro_threshold,
                engine=engine,
                share_emails=share_emails
            )
        
        # 添加搜索完成的日志
        tasks[task_id]['logs'].append(f'✓ 搜索完成: 找到 {result.get("total_searched", 0)} 位候选人')
        tasks[task_id]['logs'].append(f'✓ Flash 通过: {result.get("flash_passed", 0)} 位')
        tasks[task_id]['logs'].append(f'✓ Pro 通过: {result.get("pro_passed", 0)} 位')
        
        # 如果有 Google Sheets URL，添加到日志
        if result.get('url'):
            tasks[task_id]['logs'].append(f'✓ Google Sheets: {result.get("url")}')
        
        tasks[task_id]['progress'] = 90
        
        # 更新结果
        tasks[task_id]['status'] = 'completed'
        tasks[task_id]['progress'] = 100
        tasks[task_id]['stats'] = {
            'total_searched': result.get('total_searched', 0),
            'flash_passed': result.get('flash_passed', 0),
            'pro_passed': result.get('pro_passed', 0),
            'exported': result.get('exported', 0)
        }
        tasks[task_id]['result'] = result
        tasks[task_id]['sheet_url'] = result.get('url', '')  # 添加 Google Sheets URL
        tasks[task_id]['logs'].append('✓ 处理完成！')
        
        if result.get('url'):
            tasks[task_id]['logs'].append(f'✓ Google Sheets: {result["url"]}')
        
    except Exception as e:
        tasks[task_id]['status'] = 'failed'
        tasks[task_id]['error'] = str(e)
        tasks[task_id]['logs'].append(f'✗ 错误: {e}')


@app.route('/api/config', methods=['GET'])
def get_config():
    """获取系统配置"""
    return jsonify({
        'engines': ['serper', 'gemini', 'tavily'],
        'default_engine': 'serper',
        'default_flash_threshold': 50,
        'default_pro_threshold': 70,
        'default_search_batch': 50
    })


if __name__ == '__main__':
    # 支持云部署：从环境变量读取端口，默认 3000
    PORT = int(os.getenv('PORT', 3000))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    print("\n" + "="*70)
    print("LinkedIn 招聘系统 - Web 服务")
    print("="*70)
    print("\n启动信息:")
    print(f"  - 端口: {PORT}")
    print(f"  - 调试模式: {DEBUG}")
    if PORT == 3000:
        print(f"  - 本地地址: http://localhost:{PORT}")
    print("\n按 Ctrl+C 停止服务")
    print("="*70 + "\n")
    
    app.run(debug=DEBUG, host='0.0.0.0', port=PORT)
