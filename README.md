# OpenCode Zen API

通过 OpenCode Zen 免费使用最新 AI 模型

### 免费模型列表 (Free Series)

| 免费模型 ID | 提供商 | 说明 |
|----------|--------|------|
| `kimi-k2.5-free` | Moonshot AI | Kimi K2.5 Free (支持推理) |
| `glm-5-free` | Z.ai | GLM 5 Free (最新推荐) |
| `minimax-m2.5-free` | MiniMax | MiniMax M2.5 Free |
| `minimax-m2.1-free` | MiniMax | MiniMax M2.1 Free |
| `big-pickle` | Stealth | Big Pickle |
| `trinity-large-preview-free` | Trinity | Trinity Large Preview |

> [!TIP]
> **稳定性说明**：部分免费模型（如 `glm-5-free`）在非流式请求下可能触发上游 API 内部错误 (`prompt_tokens`)。如果遇到 500 错误，请尝试开启流式输出 (`stream: true`)。

> [!NOTE]
> 该项目仅收录官方提供的免费系列模型。

## api获取

```
从opencode zen官方获取
官网地址: https://opencode.ai
```

## 端点

```
Base URL: https://opencode.ai/zen/v1
```

| 端点 | 方法 | 说明 |
|------|------|------|
| `/models` | GET | 获取模型列表 |
| `/chat/completions` | POST | 对话补全 |

## 推理模型

GLM-4.7 和 Kimi K2.5 支持推理过程输出，通过 `reasoning_content` 字段返回思考过程。

| 字段 | 说明 |
|------|------|
| `reasoning_content` | 推理/思考过程 |
| `content` | 最终答案 |

## 使用示例

### 普通请求

```python
import requests, json, os

API_KEY = os.getenv("API_KEY")
URL = "https://opencode.ai/zen/v1/chat/completions"

resp = requests.post(
    URL,
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "glm-4.7-free",
        "messages": [{"role": "user", "content": "你好"}]
    }
)

print(resp.json()["choices"][0]["message"]["content"])
```

### 流式输出 (含推理过程)

```python
import requests, json, os

API_KEY = os.getenv("API_KEY")
URL = "https://opencode.ai/zen/v1/chat/completions"

resp = requests.post(
    URL,
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "kimi-k2.5-free",
        "messages": [{"role": "user", "content": "1+1=?"}],
        "stream": True
    },
    stream=True
)

for line in resp.iter_lines():
    if line:
        text = line.decode('utf-8')
        if text.startswith("data: ") and text[6:] != "[DONE]":
            data = json.loads(text[6:])
            delta = data["choices"][0].get("delta", {})
            
            # 推理内容 (思考过程)
            if "reasoning_content" in delta:
                print(f"💭 {delta['reasoning_content']}", end="", flush=True)
            
            # 最终回复
            if "content" in delta:
                print(delta["content"], end="", flush=True)

print()
```

## 聊天网页

项目包含一个基于 Flask 的聊天网页，支持流式输出和推理过程显示。

```bash
# 安装依赖
pip install flask requests

# 配置环境变量
echo "API_KEY=your-api-key" > .env

# 启动服务
python app.py

# 访问 http://127.0.0.1:5000
```

## 环境配置

`.env` 文件:
```
API_KEY=sk-xxxxx
```

## 免费模型说明

- 免费模型是**限时提供**的促销活动
- 免费期间数据可能用于模型训练
- 详情请参考 [OpenCode Zen 文档](https://opencode.ai/docs/zen/)

## License

MIT License
