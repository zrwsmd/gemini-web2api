"""
测试 Claude 原生 API 格式
"""
import json
import urllib.request
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("测试 Claude 原生 API 端点 (/v1/messages)")
print("=" * 60)

# Claude 原生格式请求
claude_request = {
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 1024,
    "messages": [
        {"role": "user", "content": "Say 'Hello from Claude!' in one sentence"}
    ]
}

print("\nClaude 原生格式请求:")
print(json.dumps(claude_request, indent=2, ensure_ascii=False))

try:
    req = urllib.request.Request(
        "http://localhost:8081/v1/messages",
        data=json.dumps(claude_request).encode('utf-8'),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer sk-gemini"
        },
        method='POST'
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode('utf-8'))
        print("\nClaude 原生格式响应:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        if result.get("content"):
            text = result["content"][0].get("text", "")
            print(f"\n✓ 成功！响应内容: {text}")
        else:
            print(f"\n⚠ 响应格式异常")

except urllib.error.HTTPError as e:
    error_body = e.read().decode('utf-8')
    print(f"\n✗ API 错误 ({e.code}):")
    print(error_body)

    if "Claude API key not configured" in error_body:
        print("\n提示: 需要在 config.json 中配置 claude_api_key")

except Exception as e:
    print(f"\n✗ 请求失败: {e}")

print("\n" + "=" * 60)
print("支持的三种格式:")
print("  1. OpenAI 格式 → Gemini:  /v1/chat/completions")
print("  2. OpenAI 格式 → Claude:  /v1/claude/chat/completions")
print("  3. Claude 原生格式:       /v1/messages")
print("=" * 60)
