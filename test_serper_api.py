#!/usr/bin/env python3
"""
测试 Serper API
"""

import requests
import json


def test_serper():
    """测试 Serper API"""
    print("\n" + "="*70)
    print("Serper API 测试")
    print("="*70)
    
    api_key = "d88085d4543221682eecd92082f27247f71d902f"
    url = "https://google.serper.dev/search"
    
    # 测试1: 简单查询
    print("\n测试1: 简单查询")
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'q': 'site:linkedin.com/in/ "Product Manager"',
        'num': 10
    }
    
    print(f"URL: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ 成功！")
            print(f"结果数量: {len(data.get('organic', []))}")
            if data.get('organic'):
                print(f"\n第一个结果:")
                print(json.dumps(data['organic'][0], indent=2, ensure_ascii=False))
        else:
            print(f"\n✗ 失败")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试2: 不同的 num 值
    print("\n" + "="*70)
    print("测试2: 测试不同的 num 值")
    print("="*70)
    
    for num in [10, 50, 100]:
        print(f"\n测试 num={num}...")
        payload = {
            'q': 'site:linkedin.com/in/ "Product Manager"',
            'num': num
        }
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ num={num} 成功，返回 {len(data.get('organic', []))} 个结果")
            else:
                print(f"  ✗ num={num} 失败: {response.status_code}")
                print(f"     {response.text}")
                
        except Exception as e:
            print(f"  ✗ num={num} 错误: {e}")
    
    # 测试3: 检查 API 配额
    print("\n" + "="*70)
    print("测试3: 检查 API 配额")
    print("="*70)
    
    try:
        response = requests.get(
            "https://google.serper.dev/account",
            headers={'X-API-KEY': api_key},
            timeout=10
        )
        
        if response.status_code == 200:
            account = response.json()
            print(f"✓ 账号信息:")
            print(json.dumps(account, indent=2))
        else:
            print(f"✗ 无法获取账号信息: {response.status_code}")
            
    except Exception as e:
        print(f"✗ 错误: {e}")


if __name__ == "__main__":
    test_serper()
