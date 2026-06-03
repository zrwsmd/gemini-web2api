#!/usr/bin/env python3
"""
使用示例：通过 OpenAI SDK 调用本地 Gemini API
"""
import sys
import os
# 添加本地 lib 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from openai import OpenAI

# 创建客户端，指向本地服务
client = OpenAI(
    base_url="http://localhost:8081/v1",
    api_key="sk-gemini"  # config.json 中配置的 API key
)

# 示例 1: 简单对话
print("=" * 50)
print("示例 1: 简单对话")
print("=" * 50)
response = client.chat.completions.create(
    model="gemini-3.5-flash",
    messages=[
        {"role": "user", "content": "你好，请用一句话介绍量子计算"}
    ]
)
print(f"回答: {response.choices[0].message.content}\n")

# 示例 2: 流式输出
print("=" * 50)
print("示例 2: 流式输出")
print("=" * 50)
print("问题: 写一首关于人工智能的短诗")
print("回答: ", end="", flush=True)
stream = client.chat.completions.create(
    model="gemini-3.5-flash",
    messages=[{"role": "user", "content": "写一首关于人工智能的短诗（4行）"}],
    stream=True
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
print("\n")

# 示例 3: 深度思考模式
print("=" * 50)
print("示例 3: 深度思考模式")
print("=" * 50)
response = client.chat.completions.create(
    model="gemini-3.5-flash-thinking",  # 使用 thinking 模型
    messages=[
        {"role": "user", "content": "解释为什么天空是蓝色的"}
    ]
)
print(f"回答: {response.choices[0].message.content}\n")

# 示例 4: 工具调用 (Function Calling)
print("=" * 50)
print("示例 4: 工具调用")
print("=" * 50)
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，例如：北京、上海"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="gemini-3.5-flash",
    messages=[{"role": "user", "content": "北京今天天气怎么样？"}],
    tools=tools
)

if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    print(f"调用工具: {tool_call.function.name}")
    print(f"参数: {tool_call.function.arguments}")
else:
    print(f"回答: {response.choices[0].message.content}")

print("\n" + "=" * 50)
print("所有示例执行完成！")
print("=" * 50)
