"""
完整测试 Claude 代理功能
注意: 需要在 config.json 中配置 claude_api_key 才能测试
"""
import sys
import os
import io

# 修复编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("Claude 代理功能测试")
print("=" * 60)

# 测试 1: 检查转换器
print("\n[1/3] 测试格式转换器...")
try:
    from gemini_web2api.anthropic_converter import convert_openai_to_claude

    test_request = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": "Hello"}]
    }

    claude_request = convert_openai_to_claude(test_request)
    assert claude_request["model"] == "claude-sonnet-4-20250514"
    assert len(claude_request["messages"]) > 0
    print("✓ 格式转换器工作正常")
except Exception as e:
    print(f"✗ 格式转换器错误: {e}")
    sys.exit(1)

# 测试 2: 检查配置
print("\n[2/3] 检查配置...")
try:
    from gemini_web2api.config import CONFIG, load_config

    config_path = "config.json"
    if os.path.exists(config_path):
        load_config(config_path)

        if CONFIG.get("claude_api_key"):
            print(f"✓ Claude API Key 已配置")
            can_test_api = True
        else:
            print("⚠ Claude API Key 未配置（跳过 API 测试）")
            can_test_api = False
    else:
        print("⚠ config.json 不存在（使用默认配置）")
        can_test_api = False
except Exception as e:
    print(f"✗ 配置加载错误: {e}")
    can_test_api = False

# 测试 3: 测试服务端点
print("\n[3/3] 测试服务端点...")
import urllib.request
import json

try:
    # 测试服务是否运行
    req = urllib.request.Request("http://localhost:8081/")
    with urllib.request.urlopen(req, timeout=5) as response:
        data = json.loads(response.read().decode())
        print(f"✓ 服务运行中: {data.get('status')}")
except Exception as e:
    print(f"✗ 服务未运行: {e}")
    print("\n请先启动服务: py gemini_web2api.py")
    sys.exit(1)

# 如果配置了 API Key，测试 Claude 代理端点
if can_test_api:
    print("\n[额外] 测试 Claude 代理端点...")
    try:
        test_data = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": "Say 'test' in one word"}],
            "max_tokens": 10
        }

        req = urllib.request.Request(
            "http://localhost:8081/v1/claude/chat/completions",
            data=json.dumps(test_data).encode('utf-8'),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer sk-gemini"
            },
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get("choices"):
                content = result["choices"][0]["message"]["content"]
                print(f"✓ Claude 代理工作正常")
                print(f"  响应: {content}")
            else:
                print(f"✗ 响应格式异常: {result}")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"✗ Claude 代理错误 ({e.code}): {error_body}")
    except Exception as e:
        print(f"✗ Claude 代理测试失败: {e}")
else:
    print("\n提示: 要测试 Claude 代理功能，请:")
    print("1. 在 config.json 中添加: \"claude_api_key\": \"sk-ant-api03-xxx\"")
    print("2. 重启服务")
    print("3. 重新运行此测试脚本")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
print("\n可用端点:")
print("  Gemini (免费):  http://localhost:8081/v1/chat/completions")
print("  Claude (代理):  http://localhost:8081/v1/claude/chat/completions")
print("\n详细文档: CLAUDE_PROXY_README.md")
