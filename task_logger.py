"""
自定义日志处理器 - 将 print 输出捕获到任务日志
"""
import sys
import io
from contextlib import contextmanager


class TaskLogger:
    """任务日志记录器"""
    
    def __init__(self, task_id, tasks_dict):
        self.task_id = task_id
        self.tasks = tasks_dict
        self.buffer = []
    
    def write(self, text):
        """捕获输出"""
        if text and text.strip():
            # 添加到任务日志
            if self.task_id in self.tasks:
                self.tasks[self.task_id]['logs'].append(text.strip())
        # 同时输出到终端
        sys.__stdout__.write(text)
    
    def flush(self):
        sys.__stdout__.flush()


@contextmanager
def capture_output_to_task(task_id, tasks_dict):
    """上下文管理器：捕获输出到任务日志"""
    old_stdout = sys.stdout
    sys.stdout = TaskLogger(task_id, tasks_dict)
    try:
        yield
    finally:
        sys.stdout = old_stdout
