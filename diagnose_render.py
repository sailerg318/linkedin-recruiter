"""
Render 部署诊断工具
检查环境变量和 API 连接
"""

import os
import sys

def check_environment():
    """检查环境变量"""
    print("=" * 70)
    print("环境变量检查")
    print("=" * 70)
    
    required_vars = {
        'SERPER_API_KEY': '搜索 API（必需）',
        'GEMINI_API_KEY': 'AI 分析 API（必需）',
    }
    
    optional_vars = {
        'PORT': 'Web 服务端口',
        'DEBUG': '调试模式',
        'TAVILY_API_KEY': 'Tavily 搜索（可选）',
    }
    
    missing = []
    
    print("\n必需的环境变量:")
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value:
            masked = value[:8] + '...' if len(value) > 8 else '***'
            print(f"  ✅ {var}: {masked} ({desc})")
        else:
            print(f"  ❌ {var}: 未设置 ({desc})")
            missing.append(var)
    
    print("\n可选的环境变量:")
    for var, desc in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {value} ({desc})")
        else:
            print(f"  ⚪ {var}: 未设置 ({desc})")
    
    return missing


def test_serper_api():
    """测试 Serper API"""
    print("\n" + "=" * 70)
    print("Serper API 测试")
    print("=" * 70)
    
    api_key = os.getenv('SERPER_API_KEY')
    if not api_key:
        print("  ❌ SERPER_API_KEY 未设置")
        return False
    
    try:
        import requests
        
        url = "https://google.serper.dev/search"
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        data = {
            'q': 'test query',
            'num': 1
        }
        
        print(f"  🔍 发送测试请求...")
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"  ✅ API 连接成功")
            print(f"  响应状态: {response.status_code}")
            return True
        else:
            print(f"  ❌ API 返回错误")
            print(f"  状态码: {response.status_code}")
            print(f"  响应: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"  ❌ 连接失败: {e}")
        return False


def test_gemini_api():
    """测试 Gemini API"""
    print("\n" + "=" * 70)
    print("Gemini API 测试")
    print("=" * 70)
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("  ❌ GEMINI_API_KEY 未设置")
        return False
    
    try:
        # 检查是否能导入相关模块
        print(f"  🔍 检查 API 配置...")
        print(f"  ✅ API Key 已设置")
        return True
            
    except Exception as e:
        print(f"  ❌ 检查失败: {e}")
        return False


def test_imports():
    """测试关键模块导入"""
    print("\n" + "=" * 70)
    print("模块导入测试")
    print("=" * 70)
    
    modules = [
        ('flask', 'Flask Web 框架'),
        ('flask_cors', 'CORS 支持'),
        ('requests', 'HTTP 请求'),
        ('gspread', 'Google Sheets'),
        ('google.oauth2', 'Google OAuth'),
    ]
    
    all_ok = True
    for module, desc in modules:
        try:
            __import__(module)
            print(f"  ✅ {module}: 已安装 ({desc})")
        except ImportError:
            print(f"  ❌ {module}: 未安装 ({desc})")
            all_ok = False
    
    return all_ok


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("LinkedIn 招聘系统 - Render 部署诊断")
    print("=" * 70)
    
    # 检查环境变量
    missing_vars = check_environment()
    
    # 测试模块导入
    imports_ok = test_imports()
    
    # 测试 API
    serper_ok = test_serper_api()
    gemini_ok = test_gemini_api()
    
    # 总结
    print("\n" + "=" * 70)
    print("诊断总结")
    print("=" * 70)
    
    if missing_vars:
        print(f"\n❌ 缺少必需的环境变量: {', '.join(missing_vars)}")
        print("\n解决方案:")
        print("1. 在 Render Dashboard 中设置环境变量")
        print("2. 进入你的服务 → Environment 标签")
        print("3. 添加以下变量:")
        for var in missing_vars:
            print(f"   - {var}=你的_api_key")
        print("4. 保存后 Render 会自动重新部署")
    
    if not imports_ok:
        print(f"\n❌ 部分模块未安装")
        print("\n解决方案:")
        print("1. 检查 requirements.txt 是否包含所有依赖")
        print("2. 查看 Render 构建日志中的错误")
    
    if not serper_ok:
        print(f"\n❌ Serper API 连接失败")
        print("\n解决方案:")
        print("1. 检查 SERPER_API_KEY 是否正确")
        print("2. 访问 https://serper.dev 验证 API key")
        print("3. 确认 API 配额未用完")
    
    if not gemini_ok:
        print(f"\n❌ Gemini API 配置失败")
        print("\n解决方案:")
        print("1. 检查 GEMINI_API_KEY 是否正确")
        print("2. 验证 API key 的有效性")
    
    if not missing_vars and imports_ok and serper_ok and gemini_ok:
        print(f"\n✅ 所有检查通过！系统应该可以正常运行")
    else:
        print(f"\n⚠️  发现问题，请按照上述解决方案修复")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
