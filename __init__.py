"""
LinkedIn人才搜索系统
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .tavily_search import TavilySearcher
from .candidate_filter import CandidateFilter, FilterFunctions, create_filter_from_requirements
from .feishu_table import FeishuTableClient
from .main import LinkedInRecruiter

__all__ = [
    "TavilySearcher",
    "CandidateFilter",
    "FilterFunctions",
    "create_filter_from_requirements",
    "FeishuTableClient",
    "LinkedInRecruiter"
]
