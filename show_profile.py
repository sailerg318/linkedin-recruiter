"""
展示完整的LinkedIn主页内容
"""

from tavily_search import TavilySearcher
import json


def show_full_profile():
    """展示获取到完整内容的候选人主页"""
    searcher = TavilySearcher()
    
    job_requirements = {
        "job_title": "Python Engineer",
        "keywords": "AI",
        "location": "San Francisco"
    }
    
    print("搜索中...\n")
    candidates = searcher.batch_search(job_requirements)
    
    # 找到有完整内容的候选人
    full_content_candidates = [c for c in candidates if c.get('raw_content')]
    
    if not full_content_candidates:
        print("未找到有完整内容的候选人")
        return
    
    print(f"找到 {len(full_content_candidates)} 位有完整内容的候选人\n")
    print("="*80)
    
    # 展示第一个有完整内容的候选人
    candidate = full_content_candidates[0]
    
    print(f"候选人：{candidate['name']}")
    print(f"LinkedIn：{candidate['url']}")
    print(f"职位：{candidate['title']}")
    print(f"公司：{candidate['company']}")
    print(f"地点：{candidate['location']}")
    print(f"相关度分数：{candidate['score']:.2f}")
    print("\n" + "="*80)
    print("完整主页内容：")
    print("="*80)
    print(candidate['raw_content'])
    print("="*80)
    
    # 保存到文件
    with open('full_profile.txt', 'w', encoding='utf-8') as f:
        f.write(f"候选人：{candidate['name']}\n")
        f.write(f"LinkedIn：{candidate['url']}\n")
        f.write(f"职位：{candidate['title']}\n")
        f.write(f"公司：{candidate['company']}\n")
        f.write(f"地点：{candidate['location']}\n")
        f.write(f"相关度分数：{candidate['score']:.2f}\n")
        f.write("\n" + "="*80 + "\n")
        f.write("完整主页内容：\n")
        f.write("="*80 + "\n")
        f.write(candidate['raw_content'])
    
    print(f"\n✓ 完整内容已保存到 full_profile.txt")
    
    # 也保存JSON格式
    with open('full_profile.json', 'w', encoding='utf-8') as f:
        json.dump(candidate, f, ensure_ascii=False, indent=2)
    
    print(f"✓ JSON格式已保存到 full_profile.json")


if __name__ == "__main__":
    show_full_profile()
