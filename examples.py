"""
使用示例 - 展示如何使用LinkedIn人才搜索系统
"""

from main import LinkedInRecruiter


def example_1_basic_search():
    """示例1：基础搜索 - 搜索Python工程师"""
    print("\n" + "="*60)
    print("示例1：基础搜索")
    print("="*60)
    
    recruiter = LinkedInRecruiter()
    
    job_requirements = {
        "job_title": "Python Engineer",
        "keywords": ""
    }
    
    recruiter.run_single_search(job_requirements)


def example_2_with_filters():
    """示例2：带筛选条件的搜索"""
    print("\n" + "="*60)
    print("示例2：带筛选条件的搜索")
    print("="*60)
    
    recruiter = LinkedInRecruiter()
    
    job_requirements = {
        "job_title": "AI Engineer",
        "keywords": "Machine Learning Deep Learning"
    }
    
    filter_requirements = {
        "required_keywords": ["AI", "Machine Learning"],
        "exclude_keywords": ["intern", "实习", "junior"],
        "min_score": 0.7,
        "min_experience": 5
    }
    
    recruiter.run_single_search(job_requirements, filter_requirements)


def example_3_location_company_filter():
    """示例3：按地点和公司筛选"""
    print("\n" + "="*60)
    print("示例3：按地点和公司筛选")
    print("="*60)
    
    recruiter = LinkedInRecruiter()
    
    job_requirements = {
        "job_title": "Product Manager",
        "keywords": "SaaS B2B"
    }
    
    filter_requirements = {
        "required_keywords": ["Product", "Manager"],
        "preferred_locations": ["San Francisco", "New York", "Seattle"],
        "preferred_companies": ["Google", "Microsoft", "Amazon", "Meta"],
        "min_score": 0.6
    }
    
    recruiter.run_single_search(job_requirements, filter_requirements)


def example_4_continuous_search():
    """示例4：持续搜索 - 运行5轮"""
    print("\n" + "="*60)
    print("示例4：持续搜索（5轮）")
    print("="*60)
    
    recruiter = LinkedInRecruiter()
    
    job_requirements = {
        "job_title": "Full Stack Developer",
        "keywords": "React Node.js"
    }
    
    filter_requirements = {
        "required_keywords": ["Full Stack", "React"],
        "min_score": 0.65,
        "min_experience": 3
    }
    
    # 运行5轮，每轮间隔2分钟
    recruiter.run_continuous(
        job_requirements, 
        filter_requirements, 
        max_rounds=5
    )


def example_5_data_scientist():
    """示例5：搜索数据科学家"""
    print("\n" + "="*60)
    print("示例5：搜索数据科学家")
    print("="*60)
    
    recruiter = LinkedInRecruiter()
    
    job_requirements = {
        "job_title": "Data Scientist",
        "keywords": "Python R SQL Machine Learning Statistics"
    }
    
    filter_requirements = {
        "required_keywords": ["Data", "Python", "Machine Learning"],
        "exclude_keywords": ["intern", "entry level"],
        "min_score": 0.7,
        "min_experience": 4,
        "preferred_companies": [
            "Google", "Facebook", "Amazon", "Microsoft",
            "Netflix", "Uber", "Airbnb"
        ]
    }
    
    recruiter.run_single_search(job_requirements, filter_requirements)


def example_6_frontend_developer():
    """示例6：搜索前端工程师"""
    print("\n" + "="*60)
    print("示例6：搜索前端工程师")
    print("="*60)
    
    recruiter = LinkedInRecruiter()
    
    job_requirements = {
        "job_title": "Frontend Developer",
        "keywords": "React Vue Angular TypeScript"
    }
    
    filter_requirements = {
        "required_keywords": ["Frontend", "React"],
        "min_score": 0.65,
        "min_experience": 3
    }
    
    recruiter.run_single_search(job_requirements, filter_requirements)


def example_7_devops_engineer():
    """示例7：搜索DevOps工程师"""
    print("\n" + "="*60)
    print("示例7：搜索DevOps工程师")
    print("="*60)
    
    recruiter = LinkedInRecruiter()
    
    job_requirements = {
        "job_title": "DevOps Engineer",
        "keywords": "Kubernetes Docker AWS CI/CD"
    }
    
    filter_requirements = {
        "required_keywords": ["DevOps", "Kubernetes", "AWS"],
        "exclude_keywords": ["junior", "entry"],
        "min_score": 0.7,
        "min_experience": 5
    }
    
    recruiter.run_single_search(job_requirements, filter_requirements)


def example_8_chinese_market():
    """示例8：搜索中国市场的候选人"""
    print("\n" + "="*60)
    print("示例8：搜索中国市场的候选人")
    print("="*60)
    
    recruiter = LinkedInRecruiter()
    
    job_requirements = {
        "job_title": "Python工程师",
        "keywords": "人工智能 机器学习 深度学习"
    }
    
    filter_requirements = {
        "required_keywords": ["Python", "AI"],
        "preferred_locations": ["北京", "上海", "深圳", "杭州"],
        "preferred_companies": ["阿里巴巴", "腾讯", "字节跳动", "华为"],
        "min_score": 0.65,
        "min_experience": 3
    }
    
    recruiter.run_single_search(job_requirements, filter_requirements)


if __name__ == "__main__":
    # 选择要运行的示例
    print("\n可用示例:")
    print("1. 基础搜索 - Python工程师")
    print("2. 带筛选条件 - AI工程师")
    print("3. 按地点和公司筛选 - 产品经理")
    print("4. 持续搜索5轮 - 全栈工程师")
    print("5. 数据科学家")
    print("6. 前端工程师")
    print("7. DevOps工程师")
    print("8. 中国市场候选人")
    
    choice = input("\n请选择示例编号 (1-8): ")
    
    examples = {
        "1": example_1_basic_search,
        "2": example_2_with_filters,
        "3": example_3_location_company_filter,
        "4": example_4_continuous_search,
        "5": example_5_data_scientist,
        "6": example_6_frontend_developer,
        "7": example_7_devops_engineer,
        "8": example_8_chinese_market
    }
    
    if choice in examples:
        examples[choice]()
    else:
        print("无效的选择")
