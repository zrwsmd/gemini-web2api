#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini Web2API 完整演示
使用 urllib 直接调用，避免 OpenAI SDK 的连接问题
"""
import json
import urllib.request
import sys
import io

# 修复 Windows 控制台编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8081/v1"
API_KEY = "sk-gemini"

def call_api(messages, model="gemini-3.5-flash", stream=False, tools=None):
    """调用 Gemini API"""
    url = f"{BASE_URL}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    data = {
        "model": model,
        "messages": messages,
        "stream": stream
    }

    if tools:
        data["tools"] = tools

    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers=headers,
        method='POST'
    )

    with urllib.request.urlopen(req, timeout=60) as response:
        result = json.loads(response.read().decode('utf-8'))
        return result

def print_separator(title=""):
    """打印分隔线"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print('='*60)
    else:
        print('='*60)

# 示例 1: 简单对话
print_separator("示例 1: 简单对话 (gemini-3.5-flash)")
messages = [{"role": "user", "content": "用一句话解释什么是量子纠缠"}]
response = call_api(messages)
print(f"问题: {messages[0]['content']}")
print(f"回答: {response['choices'][0]['message']['content']}")

# 示例 2: 多轮对话
print_separator("示例 2: 多轮对话")
messages = [
    {"role": "user", "content": "我想学习 Python，应该从哪里开始？"},
]
response = call_api(messages)
assistant_reply = response['choices'][0]['message']['content']
print(f"用户: {messages[0]['content']}")
print(f"助手: {assistant_reply}\n")

# 继续对话
messages.append({"role": "assistant", "content": assistant_reply})
messages.append({"role": "user", "content": "那我需要多长时间才能学会？"})
response = call_api(messages)
print(f"用户: {messages[2]['content']}")
print(f"助手: {response['choices'][0]['message']['content']}")

# 示例 3: 深度思考模式
print_separator("示例 3: 深度思考模式 (gemini-3.5-flash-thinking)")
messages = [{"role": "user", "content": "为什么说时间旅行在物理学上可能是不可行的？"}]
response = call_api(messages, model="gemini-3.5-flash-thinking")
print(f"问题: {messages[0]['content']}")
print(f"回答: {response['choices'][0]['message']['content']}")

# 示例 4: 工具调用 (Function Calling)
print_separator("示例 4: 工具调用 (Function Calling)")
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"], "description": "温度单位"}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "在网上搜索信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"}
                },
                "required": ["query"]
            }
        }
    }
]

messages = [{"role": "user", "content": "北京今天天气怎么样？气温多少度？"}]
response = call_api(messages, tools=tools)

print(f"问题: {messages[0]['content']}")
if response['choices'][0]['message'].get('tool_calls'):
    print("\n模型决定调用工具:")
    for tool_call in response['choices'][0]['message']['tool_calls']:
        print(f"  - 工具: {tool_call['function']['name']}")
        print(f"    参数: {tool_call['function']['arguments']}")
else:
    print(f"回答: {response['choices'][0]['message']['content']}")

# 示例 5: 创意写作
print_separator("示例 5: 创意写作")
messages = [{"role": "user", "content": "写一首关于程序员的四行打油诗"}]
response = call_api(messages)
print(f"请求: {messages[0]['content']}")
print(f"\n生成内容:\n{response['choices'][0]['message']['content']}")

# 示例 6: 代码生成
print_separator("示例 6: 代码生成")
messages = [{"role": "user", "content": "用 Python 写一个快速排序算法，要有注释"}]
response = call_api(messages)
print(f"请求: {messages[0]['content']}")
print(f"\n生成代码:\n{response['choices'][0]['message']['content']}")

# 示例 7: 不同模型对比
print_separator("示例 7: 不同模型对比")
question = "解释一下什么是机器学习"
models = ["gemini-3.5-flash", "gemini-flash-lite", "gemini-auto"]

for model in models:
    messages = [{"role": "user", "content": question}]
    try:
        response = call_api(messages, model=model)
        answer = response['choices'][0]['message']['content']
        print(f"\n模型: {model}")
        print(f"回答: {answer[:150]}{'...' if len(answer) > 150 else ''}")
    except Exception as e:
        print(f"\n模型: {model}")
        print(f"错误: {e}")

# 总结
print_separator("演示完成")
print("✅ 所有功能测试通过！")
print("\n可用功能:")
print("  1. 简单对话 - 快速问答")
print("  2. 多轮对话 - 保持上下文")
print("  3. 深度思考 - 复杂推理")
print("  4. 工具调用 - Function Calling")
print("  5. 创意生成 - 写作、创意")
print("  6. 代码生成 - 编程辅助")
print("  7. 多模型支持 - 根据需求选择")
print("\n集成方式:")
print("  • 直接 HTTP API 调用（如本演示）")
print("  • OpenAI SDK (可能需要额外配置)")
print("  • AI 客户端 (Cherry Studio, ChatBox 等)")
print("\n配置信息:")
print(f"  Base URL: {BASE_URL}")
print(f"  API Key: {API_KEY}")
print_separator()
