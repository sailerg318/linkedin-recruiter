"""
配置文件 - 存储API密钥和配置参数
"""

# Tavily API配置
TAVILY_API_KEY = "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"

# 飞书多维表格配置
FEISHU_APP_ID = "ycli_a901962054b8dcb5"
FEISHU_APP_SECRET = "HZxiqI12KYkO9JQeEVcB2emRiCOPY1pX"
FEISHU_TABLE_ID = "your_table_id_here"  # 多维表格ID
FEISHU_TABLE_APP_TOKEN = "your_app_token_here"  # 多维表格应用token

# 搜索配置
SEARCH_INTERVAL = 120  # 搜索间隔（秒），默认2分钟
BATCH_SIZE = 10  # 每批处理的候选人数量
MAX_SEARCH_RESULTS = 100  # 最大搜索结果数

# LinkedIn搜索关键词模板
# 支持多维度搜索：岗位、地点、公司、技能
LINKEDIN_SEARCH_TEMPLATE = 'site:linkedin.com/in/ "{job_title}" {keywords}'

# 高级搜索模板（包含location和company）
LINKEDIN_ADVANCED_SEARCH_TEMPLATE = 'site:linkedin.com/in/ "{job_title}" {location} {company} {keywords}'
