"""Anthropic Claude API proxy - converts OpenAI format to Claude format."""
import json
import time
import httpx
from typing import Optional

from .anthropic_converter import (
    convert_openai_to_claude,
    convert_claude_to_openai,
    parse_claude_stream_line
)
from .gemini import log


def call_claude_api(
    claude_request: dict,
    api_key: str,
    api_url: str = "https://api.anthropic.com/v1/messages",
    timeout: int = 180,
    stream: bool = False
):
    """
    调用 Anthropic Claude API

    Args:
        claude_request: Claude 格式的请求
        api_key: Anthropic API key
        api_url: Claude API 端点 URL
        timeout: 超时时间（秒）
        stream: 是否流式返回
    """
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }

    if stream:
        return call_claude_api_stream(claude_request, headers, api_url, timeout)
    else:
        return call_claude_api_non_stream(claude_request, headers, api_url, timeout)


def call_claude_api_non_stream(claude_request: dict, headers: dict, api_url: str, timeout: int):
    """非流式调用 Claude API"""
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.post(api_url, json=claude_request, headers=headers)

            if response.status_code != 200:
                error_text = response.text
                log(f"Claude API error ({response.status_code}): {error_text}")
                raise Exception(f"Claude API error ({response.status_code}): {error_text}")

            return response.json()
    except httpx.TimeoutException:
        log("Claude API request timed out")
        raise Exception("Claude API request timed out")
    except httpx.RequestError as e:
        log(f"Claude API request error: {e}")
        raise Exception(f"Claude API request error: {e}")


def call_claude_api_stream(claude_request: dict, headers: dict, api_url: str, timeout: int):
    """流式调用 Claude API - 返回生成器"""
    try:
        with httpx.Client(timeout=timeout) as client:
            with client.stream("POST", api_url, json=claude_request, headers=headers) as response:
                if response.status_code != 200:
                    error_text = response.text
                    log(f"Claude API stream error ({response.status_code}): {error_text}")
                    raise Exception(f"Claude API error ({response.status_code}): {error_text}")

                # 逐行读取 SSE 流
                for line in response.iter_lines():
                    if line:
                        yield line
    except httpx.TimeoutException:
        log("Claude API stream timed out")
        raise Exception("Claude API stream timed out")
    except httpx.RequestError as e:
        log(f"Claude API stream error: {e}")
        raise Exception(f"Claude API stream error: {e}")


def convert_claude_stream_to_openai(
    stream_lines,
    original_model: str,
    chat_id: str
):
    """
    将 Claude 流式响应转换为 OpenAI 流式格式

    Args:
        stream_lines: Claude SSE 流的行迭代器
        original_model: 原始请求的模型名
        chat_id: 对话 ID
    """
    created = int(time.time())
    sent_role = False
    current_tool_call_index = 0

    for line in stream_lines:
        event = parse_claude_stream_line(line)
        if not event:
            continue

        event_type = event.get("type", "")

        if event_type == "done":
            yield f"data: [DONE]\n\n"
            return

        if event_type == "message_start":
            # 发送初始 chunk（包含 role）
            if not sent_role:
                chunk = {
                    "id": chat_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": original_model,
                    "choices": [{
                        "index": 0,
                        "delta": {"role": "assistant", "content": ""},
                        "finish_reason": None
                    }]
                }
                yield f"data: {json.dumps(chunk)}\n\n"
                sent_role = True

        elif event_type == "content_block_start":
            content_block = event.get("content_block", {})
            block_type = content_block.get("type", "")

            if block_type == "tool_use":
                tool_id = content_block.get("id", f"call_{time.time()}")
                tool_name = content_block.get("name", "")

                chunk = {
                    "id": chat_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": original_model,
                    "choices": [{
                        "index": 0,
                        "delta": {
                            "tool_calls": [{
                                "index": current_tool_call_index,
                                "id": tool_id,
                                "type": "function",
                                "function": {"name": tool_name, "arguments": ""}
                            }]
                        },
                        "finish_reason": None
                    }]
                }
                yield f"data: {json.dumps(chunk)}\n\n"

        elif event_type == "content_block_delta":
            delta = event.get("delta", {})
            delta_type = delta.get("type", "")

            if delta_type == "text_delta":
                text = delta.get("text", "")
                if text:
                    chunk = {
                        "id": chat_id,
                        "object": "chat.completion.chunk",
                        "created": created,
                        "model": original_model,
                        "choices": [{
                            "index": 0,
                            "delta": {"content": text},
                            "finish_reason": None
                        }]
                    }
                    yield f"data: {json.dumps(chunk)}\n\n"

            elif delta_type == "input_json_delta":
                partial_json = delta.get("partial_json", "")
                if partial_json:
                    chunk = {
                        "id": chat_id,
                        "object": "chat.completion.chunk",
                        "created": created,
                        "model": original_model,
                        "choices": [{
                            "index": 0,
                            "delta": {
                                "tool_calls": [{
                                    "index": current_tool_call_index,
                                    "function": {"arguments": partial_json}
                                }]
                            },
                            "finish_reason": None
                        }]
                    }
                    yield f"data: {json.dumps(chunk)}\n\n"

        elif event_type == "content_block_stop":
            current_tool_call_index += 1

        elif event_type == "message_delta":
            delta = event.get("delta", {})
            stop_reason = delta.get("stop_reason")

            if stop_reason:
                finish_reason_map = {
                    "end_turn": "stop",
                    "stop_sequence": "stop",
                    "max_tokens": "length",
                    "tool_use": "tool_calls"
                }
                finish_reason = finish_reason_map.get(stop_reason, "stop")

                chunk = {
                    "id": chat_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": original_model,
                    "choices": [{
                        "index": 0,
                        "delta": {},
                        "finish_reason": finish_reason
                    }]
                }
                yield f"data: {json.dumps(chunk)}\n\n"

        elif event_type == "message_stop":
            yield f"data: [DONE]\n\n"
            return

        elif event_type == "error":
            error = event.get("error", {})
            error_msg = error.get("message", "Unknown error")
            log(f"Claude stream error: {error_msg}")

            chunk = {
                "id": chat_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": original_model,
                "choices": [{
                    "index": 0,
                    "delta": {"content": f"\n\n[Error: {error_msg}]"},
                    "finish_reason": "stop"
                }]
            }
            yield f"data: {json.dumps(chunk)}\n\n"
            yield f"data: [DONE]\n\n"
            return

    # 确保发送 DONE
    yield f"data: [DONE]\n\n"
