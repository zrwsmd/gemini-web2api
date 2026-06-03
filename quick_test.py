"""
简单测试脚本 - 不依赖 OpenAI SDK
直接使用 requests 库测试 API
"""
import json
import sys
import os
import io

# 修复 Windows 控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 尝试导入 requests，如果没有就用 urllib
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    HAS_REQUESTS = False

def test_with_requests():
    """使用 requests 库测试"""
    url = "http://localhost:8081/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-gemini"
    }
    data = {
        "model": "gemini-3.5-flash",
        "messages": [
            {"role": "user", "content": "用一句话介绍你自己"}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print("✅ 测试成功！")
            print(f"回答: {result['choices'][0]['message']['content']}")
            return True
        else:
            print(f"❌ 测试失败: HTTP {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ 连接错误: {e}")
        return False

def test_with_urllib():
    """使用 urllib 测试"""
    import urllib.request
    import json

    url = "http://localhost:8081/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-gemini"
    }
    data = {
        "model": "gemini-3.5-flash",
        "messages": [
            {"role": "user", "content": "用一句话介绍你自己"}
        ]
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            print("✅ 测试成功！")
            print(f"回答: {result['choices'][0]['message']['content']}")
            return True
    except Exception as e:
        print(f"❌ 连接错误: {e}")
        return False

def check_service():
    """检查服务是否运行"""
    try:
        if HAS_REQUESTS:
            response = requests.get("http://localhost:8081/", timeout=5)
        else:
            with urllib.request.urlopen("http://localhost:8081/", timeout=5) as response:
                pass
        print("✅ 服务正在运行")
        return True
    except Exception as e:
        print(f"❌ 服务未启动或无法访问: {e}")
        print("\n请先启动服务:")
        print("  方法1: py gemini_web2api.py")
        print("  方法2（需要代理）: py gemini_web2api.py --proxy http://127.0.0.1:7890")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Gemini Web2API 测试脚本")
    print("=" * 60)
    print()

    # 步骤1: 检查服务
    print("步骤 1/2: 检查服务状态...")
    if not check_service():
        sys.exit(1)
    print()

    # 步骤2: 测试 API
    print("步骤 2/2: 测试 API 调用...")
    print("提示: 如果失败，可能需要配置代理访问 Google Gemini")
    print()

    if HAS_REQUESTS:
        success = test_with_requests()
    else:
        success = test_with_urllib()

    print()
    print("=" * 60)
    if success:
        print("✅ 全部测试通过！服务可以正常使用")
        print()
        print("下一步:")
        print("1. 在 AI 客户端中配置:")
        print("   Base URL: http://localhost:8081/v1")
        print("   API Key: sk-gemini")
        print("   Model: gemini-3.5-flash")
        print()
        print("2. 或使用 Python 代码调用（参考 test_example.py）")
    else:
        print("❌ 测试失败")
        print()
        print("可能的原因:")
        print("1. 无法访问 gemini.google.com（需要配置代理）")
        print("2. 服务配置有误")
        print()
        print("解决方案:")
        print("1. 重启服务并配置代理:")
        print("   py gemini_web2api.py --proxy http://127.0.0.1:7890")
        print()
        print("2. 或修改 config.json 添加代理配置:")
        print('   "proxy": "http://127.0.0.1:7890"')
    print("=" * 60)
