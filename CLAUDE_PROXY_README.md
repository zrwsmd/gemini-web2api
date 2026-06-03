# OpenAI 到 Claude 格式转换功能使用说明

## 功能介绍

这个项目现在支持将 OpenAI 格式的请求转换为 Anthropic Claude API 格式，让你可以：
- 使用 OpenAI SDK 或客户端调用 Claude API
- 在支持 OpenAI 格式的工具中使用 Claude 模型
- 无缝切换 Gemini 和 Claude 后端

## 端点说明

### 1. Gemini 服务（默认）
- 端点: `/v1/chat/completions`
- 后端: Google Gemini（免费，无需 API Key）
- 用途: 日常使用，免费方案

### 2. Claude 代理服务（新增）
- 端点: `/v1/claude/chat/completions`
- 后端: Anthropic Claude（需要 Claude API Key）
- 用途: 需要使用 Claude 模型时

## 配置方法

### 1. 修改 config.json

在 config.json 中添加 Claude API Key：

```json
{
  "port": 8081,
  "host": "0.0.0.0",
  "api_keys": ["sk-gemini"],
  "claude_api_key": "sk-ant-api03-xxxxx",
  "claude_api_url": "https://api.anthropic.com/v1/messages"
}
```

配置说明：
- `claude_api_key`: 你的 Anthropic API Key（从 https://console.anthropic.com 获取）
- `claude_api_url`: Claude API 端点（默认即可，除非使用第三方代理）

### 2. 获取 Claude API Key

1. 访问 https://console.anthropic.com
2. 注册/登录账号
3. 进入 API Keys 页面
4. 创建新的 API Key
5. 复制 Key 到 config.json

## 使用方法

### 方法 1: curl 测试

调用 Gemini（免费）：
```bash
curl http://localhost:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-gemini" \
  -d "{\"model\":\"gemini-3.5-flash\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello\"}]}"
```

调用 Claude（需要 API Key）：
```bash
curl http://localhost:8081/v1/claude/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-gemini" \
  -d "{\"model\":\"gpt-4\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello\"}]}"
```

### 方法 2: Python SDK

```python
from openai import OpenAI

# 使用 Gemini（免费）
client_gemini = OpenAI(
    base_url="http://localhost:8081/v1",
    api_key="sk-gemini"
)

response = client_gemini.chat.completions.create(
    model="gemini-3.5-flash",
    messages=[{"role": "user", "content": "你好"}]
)
print(response.choices[0].message.content)

# 使用 Claude（通过代理）
client_claude = OpenAI(
    base_url="http://localhost:8081/v1/claude",
    api_key="sk-gemini"
)

response = client_claude.chat.completions.create(
    model="gpt-4",  # 会自动转换为 claude-sonnet-4
    messages=[{"role": "user", "content": "你好"}]
)
print(response.choices[0].message.content)
```

### 方法 3: AI 客户端配置

在 AI 客户端中可以添加两个配置：

配置 1 - Gemini（免费）：
```
名称: Gemini Free
Base URL: http://localhost:8081/v1
API Key: sk-gemini
模型: gemini-3.5-flash
```

配置 2 - Claude（通过本地代理）：
```
名称: Claude Proxy
Base URL: http://localhost:8081/v1/claude
API Key: sk-gemini
模型: gpt-4 或 gpt-3.5-turbo
```

## 模型映射

当使用 `/v1/claude/chat/completions` 端点时，模型名会自动转换：

| OpenAI 模型 | Claude 模型 |
|------------|-------------|
| gpt-4 | claude-sonnet-4-20250514 |
| gpt-4-turbo | claude-sonnet-4-20250514 |
| gpt-4o | claude-sonnet-4-20250514 |
| gpt-3.5-turbo | claude-3-5-haiku-20241022 |
| gpt-3.5 | claude-3-5-haiku-20241022 |

你也可以直接使用 Claude 模型名：
- `claude-sonnet-4-20250514`
- `claude-3-5-sonnet-20241022`
- `claude-3-5-haiku-20241022`
- 等等

## 功能支持

支持的功能：
- 普通对话
- 流式输出
- 工具调用（Function Calling）
- 多轮对话
- System 消息
- 温度控制等参数

## 成本对比

| 方案 | 成本 | 优点 | 缺点 |
|------|------|------|------|
| Gemini (直接) | 免费 | 完全免费，无需 API Key | 可能有频率限制 |
| Claude (代理) | 按使用付费 | 官方 API，稳定可靠 | 需要付费 |

## 常见问题

### 1. Claude API Key 错误

错误: `Claude API key not configured`

解决: 确保在 config.json 中正确配置了 `claude_api_key`

### 2. Claude API 调用失败

错误: `Claude proxy error: ...`

可能原因：
- API Key 无效或过期
- API 配额不足
- 网络连接问题

解决: 检查 API Key，查看 Anthropic 控制台的使用情况

### 3. 如何切换后端？

方法 1: 更改 Base URL
- Gemini: `http://localhost:8081/v1`
- Claude: `http://localhost:8081/v1/claude`

方法 2: 在代码中动态切换
```python
# 根据需求选择后端
backend = "gemini"  # 或 "claude"
base_url = f"http://localhost:8081/v1/{backend if backend == 'claude' else ''}"
```

## 优势

1. 统一接口
   - 使用相同的 OpenAI SDK
   - 无需修改现有代码
   - 轻松切换后端

2. 成本优化
   - 免费任务用 Gemini
   - 重要任务用 Claude
   - 灵活分配资源

3. 功能完整
   - 支持流式输出
   - 支持工具调用
   - 支持所有 Claude 模型

## 下一步

1. 获取 Claude API Key（可选）
2. 更新 config.json 配置
3. 重启服务
4. 测试两个端点
5. 在你的应用中使用
