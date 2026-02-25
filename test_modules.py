"""
单元测试 - 测试各个模块的功能
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from candidate_filter import (
    CandidateFilter, 
    FilterFunctions, 
    create_filter_from_requirements
)


class TestCandidateFilter(unittest.TestCase):
    """测试候选人筛选器"""
    
    def setUp(self):
        """测试前准备"""
        self.test_candidates = [
            {
                "name": "张三",
                "title": "Senior Python Engineer at Google",
                "snippet": "5年Python开发经验，专注于AI和机器学习",
                "score": 0.85,
                "url": "https://linkedin.com/in/zhangsan"
            },
            {
                "name": "李四",
                "title": "Junior Developer",
                "snippet": "1年开发经验",
                "score": 0.45,
                "url": "https://linkedin.com/in/lisi"
            },
            {
                "name": "王五",
                "title": "Python Developer at Alibaba",
                "snippet": "3年Python经验，熟悉Django和Flask",
                "score": 0.75,
                "url": "https://linkedin.com/in/wangwu"
            }
        ]
    
    def test_keyword_in_title(self):
        """测试职位标题关键词筛选"""
        filter_func = FilterFunctions.keyword_in_title(["Python"])
        
        self.assertTrue(filter_func(self.test_candidates[0]))
        self.assertFalse(filter_func(self.test_candidates[1]))
        self.assertTrue(filter_func(self.test_candidates[2]))
    
    def test_keyword_in_snippet(self):
        """测试简介关键词筛选"""
        filter_func = FilterFunctions.keyword_in_snippet(["AI"])
        
        self.assertTrue(filter_func(self.test_candidates[0]))
        self.assertFalse(filter_func(self.test_candidates[1]))
        self.assertFalse(filter_func(self.test_candidates[2]))
    
    def test_exclude_keywords(self):
        """测试排除关键词"""
        filter_func = FilterFunctions.exclude_keywords(["Junior"])
        
        self.assertTrue(filter_func(self.test_candidates[0]))
        self.assertFalse(filter_func(self.test_candidates[1]))
        self.assertTrue(filter_func(self.test_candidates[2]))
    
    def test_min_score(self):
        """测试最低分数筛选"""
        filter_func = FilterFunctions.min_score(0.7)
        
        self.assertTrue(filter_func(self.test_candidates[0]))
        self.assertFalse(filter_func(self.test_candidates[1]))
        self.assertTrue(filter_func(self.test_candidates[2]))
    
    def test_has_experience(self):
        """测试工作年限筛选"""
        filter_func = FilterFunctions.has_experience(3)
        
        self.assertTrue(filter_func(self.test_candidates[0]))  # 5年
        self.assertFalse(filter_func(self.test_candidates[1]))  # 1年
        self.assertTrue(filter_func(self.test_candidates[2]))  # 3年
    
    def test_filter_candidates(self):
        """测试完整筛选流程"""
        filter_obj = CandidateFilter()
        filter_obj.add_filter(FilterFunctions.min_score(0.7))
        filter_obj.add_filter(FilterFunctions.keyword_in_title(["Python"]))
        
        filtered = filter_obj.filter_candidates(self.test_candidates, batch_size=10)
        
        # 应该只有张三和王五通过
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0]["name"], "张三")
        self.assertEqual(filtered[1]["name"], "王五")
    
    def test_create_filter_from_requirements(self):
        """测试从需求创建筛选器"""
        requirements = {
            "required_keywords": ["Python"],
            "min_score": 0.7,
            "min_experience": 3
        }
        
        filter_obj = create_filter_from_requirements(requirements)
        filtered = filter_obj.filter_candidates(self.test_candidates, batch_size=10)
        
        # 应该只有张三和王五通过
        self.assertEqual(len(filtered), 2)


class TestTavilySearcher(unittest.TestCase):
    """测试Tavily搜索器"""
    
    @patch('tavily_search.requests.post')
    def test_search_linkedin_candidates(self, mock_post):
        """测试LinkedIn候选人搜索"""
        # 模拟API响应
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "url": "https://linkedin.com/in/john-doe",
                    "title": "Python Engineer at Google",
                    "content": "5 years of Python experience",
                    "score": 0.85
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        from tavily_search import TavilySearcher
        searcher = TavilySearcher()
        
        results = searcher.search_linkedin_candidates(
            job_title="Python Engineer",
            keywords="AI"
        )
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "John Doe")
        self.assertIn("linkedin.com", results[0]["url"])


class TestFeishuTableClient(unittest.TestCase):
    """测试飞书表格客户端"""
    
    @patch('feishu_table.requests.post')
    def test_get_tenant_access_token(self, mock_post):
        """测试获取访问令牌"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": 0,
            "tenant_access_token": "test_token",
            "expire": 7200
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        from feishu_table import FeishuTableClient
        client = FeishuTableClient()
        
        token = client._get_tenant_access_token()
        
        self.assertEqual(token, "test_token")
        self.assertIsNotNone(client.access_token)
    
    @patch('feishu_table.requests.post')
    def test_add_records(self, mock_post):
        """测试添加记录"""
        # 模拟两次请求：获取token和添加记录
        mock_responses = [
            Mock(json=lambda: {"code": 0, "tenant_access_token": "test_token", "expire": 7200}),
            Mock(json=lambda: {"code": 0})
        ]
        
        for resp in mock_responses:
            resp.raise_for_status = Mock()
        
        mock_post.side_effect = mock_responses
        
        from feishu_table import FeishuTableClient
        client = FeishuTableClient()
        
        test_candidates = [
            {
                "name": "测试",
                "url": "https://linkedin.com/in/test",
                "title": "Engineer",
                "snippet": "Test",
                "score": 0.8
            }
        ]
        
        result = client.add_records(test_candidates)
        
        self.assertTrue(result)


def run_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("运行单元测试")
    print("="*60 + "\n")
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestCandidateFilter))
    suite.addTests(loader.loadTestsFromTestCase(TestTavilySearcher))
    suite.addTests(loader.loadTestsFromTestCase(TestFeishuTableClient))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果
    print("\n" + "="*60)
    print("测试结果")
    print("="*60)
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
