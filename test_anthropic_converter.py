"""
测试 OpenAI 到 Anthropic 格式转换的脚本
"""
import json
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from gemini_web2api.anthropic_converter import (
    convert_openai_to_claude,
    convert_claude_to_openai
)

# 测试 1: 简单对话转换
print("=" * 60)
print("测试 1: 简单对话")
print("=" * 60)

openai_request = {
    "model": "gpt-4",
    "messages": [
        {"role": "system", "content": "你是一个有帮助的助手"},
        {"role": "user", "content": "你好"}
    ],
    "max_tokens": 1000
}

claude_request = convert_openai_to_claude(openai_request)
print("\nOpenAI 请求:")
print(json.dumps(openai_request, indent=2, ensure_ascii=False))
print("\n转换为 Claude 请求:")
print(json.dumps(claude_request, indent=2, ensure_ascii=False))

# 测试 2: 工具调用转换
print("\n" + "=" * 60)
print("测试 2: 工具调用")
print("=" * 60)

openai_request_tools = {
    "model": "gpt-4",
    "messages": [
        {"role": "user", "content": "北京天气怎么样?"}
    ],
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "获取天气信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string", "description": "城市名"}
                    },
                    "required": ["city"]
                }
            }
        }
    ],
    "tool_choice": "auto"
}

claude_request_tools = convert_openai_to_claude(openai_request_tools)
print("\nOpenAI 请求 (带工具):")
print(json.dumps(openai_request_tools, indent=2, ensure_ascii=False))
print("\n转换为 Claude 请求:")
print(json.dumps(claude_request_tools, indent=2, ensure_ascii=False))

# 测试 3: Claude 响应转回 OpenAI 格式
print("\n" + "=" * 60)
print("测试 3: Claude 响应转换")
print("=" * 60)

claude_response = {
    "id": "msg_123456",
    "type": "message",
    "role": "assistant",
    "content": [
        {"type": "text", "text": "你好！我是 Claude，很高兴为你服务。"}
    ],
    "stop_reason": "end_turn",
    "usage": {
        "input_tokens": 20,
        "output_tokens": 15
    }
}

openai_response = convert_claude_to_openai(claude_response, "gpt-4")
print("\nClaude 响应:")
print(json.dumps(claude_response, indent=2, ensure_ascii=False))
print("\n转换为 OpenAI 响应:")
print(json.dumps(openai_response, indent=2, ensure_ascii=False))

# 测试 4: 带工具调用的 Claude 响应
print("\n" + "=" * 60)
print("测试 4: Claude 工具调用响应转换")
print("=" * 60)

claude_response_tool = {
    "id": "msg_789",
    "type": "message",
    "role": "assistant",
    "content": [
        {"type": "text", "text": "让我查一下北京的天气。"},
        {
            "type": "tool_use",
            "id": "toolu_123",
            "name": "get_weather",
            "input": {"city": "北京"}
        }
    ],
    "stop_reason": "tool_use",
    "usage": {
        "input_tokens": 30,
        "output_tokens": 20
    }
}

openai_response_tool = convert_claude_to_openai(claude_response_tool, "gpt-4")
print("\nClaude 响应 (带工具调用):")
print(json.dumps(claude_response_tool, indent=2, ensure_ascii=False))
print("\n转换为 OpenAI 响应:")
print(json.dumps(openai_response_tool, indent=2, ensure_ascii=False))

print("\n" + "=" * 60)
print("所有测试完成！")
print("=" * 60)
