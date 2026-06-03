"""OpenAI to Anthropic/Claude API format converter."""
import json
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union


def convert_model_name_to_claude(model: str) -> str:
    """Convert OpenAI model names to Claude model names."""
    model_mapping = {
        "gpt-4": "claude-sonnet-4-20250514",
        "gpt-4-turbo": "claude-sonnet-4-20250514",
        "gpt-4o": "claude-sonnet-4-20250514",
        "gpt-3.5-turbo": "claude-3-5-haiku-20241022",
        "gpt-3.5": "claude-3-5-haiku-20241022",
    }

    # If already a Claude model, pass through
    if model.startswith("claude-"):
        return model

    # Try to map, otherwise use default
    return model_mapping.get(model, "claude-sonnet-4-20250514")


def convert_content_to_claude(content: Union[str, List[Dict[str, Any]], None]) -> Union[str, List[Dict[str, Any]]]:
    """Convert OpenAI content format to Claude format."""
    if content is None:
        return ""

    if isinstance(content, str):
        return content

    if not isinstance(content, list):
        return str(content)

    claude_content = []
    for part in content:
        if isinstance(part, str):
            claude_content.append({"type": "text", "text": part})
        elif isinstance(part, dict):
            part_type = part.get("type", "text")

            if part_type == "text":
                text = part.get("text", "")
                if text:
                    claude_content.append({"type": "text", "text": text})

            elif part_type == "image_url":
                image_url = part.get("image_url", {})
                url = image_url.get("url", "") if isinstance(image_url, dict) else str(image_url)

                if url.startswith("data:"):
                    # Parse base64 data URL
                    try:
                        header, data = url.split(",", 1)
                        media_type = header.split(";")[0].replace("data:", "")
                        claude_content.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": data
                            }
                        })
                    except Exception:
                        pass
                else:
                    # URL-based image
                    claude_content.append({
                        "type": "image",
                        "source": {
                            "type": "url",
                            "url": url
                        }
                    })

    return claude_content if claude_content else ""


def extract_system_message(messages: List[Dict[str, Any]]) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    """Extract system message from messages list."""
    system_content = []
    other_messages = []

    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")

        if role == "system":
            if isinstance(content, str):
                system_content.append(content)
            elif isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        system_content.append(part.get("text", ""))
                    elif isinstance(part, str):
                        system_content.append(part)
        else:
            other_messages.append(msg)

    system_text = "\n\n".join(system_content) if system_content else None
    return system_text, other_messages


def convert_messages_to_claude(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert OpenAI messages to Claude format."""
    claude_messages = []

    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content")

        # Map roles
        if role == "assistant":
            claude_role = "assistant"
        elif role == "tool":
            claude_role = "user"
        elif role == "function":
            claude_role = "user"
        else:
            claude_role = "user"

        # Handle tool/function results
        if role == "tool" or role == "function":
            tool_call_id = msg.get("tool_call_id") or msg.get("name", f"tool_{uuid.uuid4().hex[:8]}")
            result_content = str(content) if content else ""
            is_error = msg.get("is_error", False)

            claude_content = [{
                "type": "tool_result",
                "tool_use_id": tool_call_id,
                "content": result_content,
                **({"is_error": True} if is_error else {})
            }]

        # Handle assistant messages with tool calls
        elif role == "assistant" and msg.get("tool_calls"):
            claude_content = []
            if content:
                converted = convert_content_to_claude(content)
                if isinstance(converted, str) and converted:
                    claude_content.append({"type": "text", "text": converted})
                elif isinstance(converted, list):
                    claude_content.extend(converted)

            for tool_call in msg.get("tool_calls", []):
                func = tool_call.get("function", {})
                try:
                    args = json.loads(func.get("arguments", "{}"))
                except json.JSONDecodeError:
                    args = {}

                claude_content.append({
                    "type": "tool_use",
                    "id": tool_call.get("id", f"toolu_{uuid.uuid4().hex[:24]}"),
                    "name": func.get("name", "unknown"),
                    "input": args
                })
        else:
            # Regular message
            claude_content = convert_content_to_claude(content)

        # Handle empty content
        if not claude_content:
            if claude_role == "assistant":
                claude_content = ""
            else:
                claude_content = " "

        # Merge consecutive messages with same role
        if claude_messages and claude_messages[-1]["role"] == claude_role:
            existing_content = claude_messages[-1]["content"]
            if isinstance(existing_content, str) and isinstance(claude_content, str):
                claude_messages[-1]["content"] = existing_content + "\n\n" + claude_content
            elif isinstance(existing_content, list) and isinstance(claude_content, list):
                claude_messages[-1]["content"].extend(claude_content)
            elif isinstance(existing_content, str) and isinstance(claude_content, list):
                claude_messages[-1]["content"] = [{"type": "text", "text": existing_content}] + claude_content
            elif isinstance(existing_content, list) and isinstance(claude_content, str):
                claude_messages[-1]["content"].append({"type": "text", "text": claude_content})
        else:
            claude_messages.append({
                "role": claude_role,
                "content": claude_content
            })

    # Ensure messages alternate and start with user
    if claude_messages and claude_messages[0]["role"] != "user":
        claude_messages.insert(0, {"role": "user", "content": "Continue."})

    return claude_messages


def convert_tools_to_claude(
    tools: Optional[List[Dict[str, Any]]] = None,
    functions: Optional[List[Dict[str, Any]]] = None
) -> Optional[List[Dict[str, Any]]]:
    """Convert OpenAI tools/functions to Claude format."""
    claude_tools = []

    if tools:
        for tool in tools:
            if tool.get("type") == "function":
                func = tool.get("function", {})
                claude_tool = {
                    "name": func.get("name", ""),
                    "description": func.get("description", ""),
                    "input_schema": func.get("parameters", {"type": "object", "properties": {}})
                }
                claude_tools.append(claude_tool)

    if functions:
        for func in functions:
            claude_tool = {
                "name": func.get("name", ""),
                "description": func.get("description", ""),
                "input_schema": func.get("parameters", {"type": "object", "properties": {}})
            }
            claude_tools.append(claude_tool)

    return claude_tools if claude_tools else None


def convert_tool_choice_to_claude(
    tool_choice: Optional[Union[str, Dict[str, Any]]],
    has_tools: bool
) -> Optional[Dict[str, Any]]:
    """Convert OpenAI tool_choice to Claude format."""
    if tool_choice is None or not has_tools:
        return None

    if isinstance(tool_choice, str):
        if tool_choice == "auto":
            return {"type": "auto"}
        elif tool_choice == "none":
            return None
        elif tool_choice == "required":
            return {"type": "any"}
    elif isinstance(tool_choice, dict):
        if tool_choice.get("type") == "function":
            func_name = tool_choice.get("function", {}).get("name", "")
            if func_name:
                return {"type": "tool", "name": func_name}

    return {"type": "auto"}


def convert_openai_to_claude(request: Dict[str, Any]) -> Dict[str, Any]:
    """Convert OpenAI request to Claude request format."""
    messages = request.get("messages", [])

    # Extract system message
    system_text, other_messages = extract_system_message(messages)

    # Convert messages
    claude_messages = convert_messages_to_claude(other_messages)

    # Get the model
    model = convert_model_name_to_claude(request.get("model", "gpt-4"))

    # Get max_tokens - Claude requires this
    max_tokens = request.get("max_tokens", 4096)

    # Build Claude request
    claude_request: Dict[str, Any] = {
        "model": model,
        "messages": claude_messages,
        "max_tokens": max_tokens
    }

    # Add system message
    if system_text:
        claude_request["system"] = system_text

    # Add optional parameters
    if request.get("temperature") is not None:
        temp = request["temperature"]
        claude_request["temperature"] = min(max(float(temp), 0.0), 1.0)

    if request.get("top_p") is not None:
        claude_request["top_p"] = float(request["top_p"])

    if request.get("stream"):
        claude_request["stream"] = True

    # Convert stop sequences
    stop = request.get("stop")
    if stop:
        if isinstance(stop, str):
            claude_request["stop_sequences"] = [stop]
        elif isinstance(stop, list):
            claude_request["stop_sequences"] = [str(s) for s in stop]

    # Convert tools
    claude_tools = convert_tools_to_claude(
        request.get("tools"),
        request.get("functions")
    )
    if claude_tools:
        claude_request["tools"] = claude_tools

    # Convert tool choice
    tool_choice = request.get("tool_choice") or request.get("function_call")
    if tool_choice:
        claude_tool_choice = convert_tool_choice_to_claude(tool_choice, bool(claude_tools))
        if claude_tool_choice:
            claude_request["tool_choice"] = claude_tool_choice

    # Add metadata
    if request.get("user"):
        claude_request["metadata"] = {"user_id": request["user"]}

    return claude_request


def convert_claude_to_openai(claude_response: Dict[str, Any], original_model: str) -> Dict[str, Any]:
    """Convert Claude response to OpenAI response format."""
    # Extract content
    content_blocks = claude_response.get("content", [])
    text_parts = []
    tool_calls = []

    for block in content_blocks:
        block_type = block.get("type", "")

        if block_type == "text":
            text_parts.append(block.get("text", ""))
        elif block_type == "tool_use":
            tool_calls.append({
                "id": block.get("id", f"call_{uuid.uuid4().hex[:24]}"),
                "type": "function",
                "function": {
                    "name": block.get("name", ""),
                    "arguments": json.dumps(block.get("input", {}))
                }
            })

    text_content = "".join(text_parts)

    # Map stop reason
    stop_reason = claude_response.get("stop_reason", "end_turn")
    finish_reason_map = {
        "end_turn": "stop",
        "stop_sequence": "stop",
        "max_tokens": "length",
        "tool_use": "tool_calls"
    }
    finish_reason = finish_reason_map.get(stop_reason, "stop")

    # Build message
    message: Dict[str, Any] = {
        "role": "assistant",
        "content": text_content if text_content else None
    }

    if tool_calls:
        message["tool_calls"] = tool_calls
        if not text_content:
            message["content"] = None

    # Build usage info
    usage = claude_response.get("usage", {})

    return {
        "id": f"chatcmpl-{claude_response.get('id', uuid.uuid4().hex)}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": original_model,
        "choices": [{
            "index": 0,
            "message": message,
            "finish_reason": finish_reason
        }],
        "usage": {
            "prompt_tokens": usage.get("input_tokens", 0),
            "completion_tokens": usage.get("output_tokens", 0),
            "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
        }
    }


def parse_claude_stream_line(line: str) -> Optional[Dict[str, Any]]:
    """Parse a single line from Claude SSE stream."""
    if not line or not line.strip():
        return None

    # Skip event: lines
    if line.startswith("event:"):
        return None

    if not line.startswith("data:"):
        return None

    data = line[5:].strip()

    if data == "[DONE]":
        return {"type": "done"}

    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None
