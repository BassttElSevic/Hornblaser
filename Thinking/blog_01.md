# Blog_01

---

<a id="toc-top"></a>

## 目录

- [Blog\_01](#blog_01)
  - [目录](#目录)
  - [全景树](#全景树)
  - [构造参数：client](#构造参数client)
  - [得到回复](#得到回复)
  - [结合结构树的节选来讲解](#结合结构树的节选来讲解)
    - [为什么直接打印 response 是一大坨？](#为什么直接打印-response-是一大坨)
    - [讲解](#讲解)
      - [参数](#参数)
    - [回到那颗树](#回到那颗树)

---

<a id="toc-全景树"></a>

## 全景树

这里只是参考，没必要一口气全部搞懂，我建议你先看下面的

```
openai.OpenAI(api_key="sk-...")
│
├── 📋 构造参数（实例化时注入）
│   ├── api_key: str | Callable[[], str] | None
│   ├── admin_api_key: str | None
│   ├── workload_identity: WorkloadIdentity | None
│   ├── organization: str | None          # 多组织场景
│   ├── project: str | None               # 项目隔离
│   ├── webhook_secret: str | None
│   ├── base_url: str | httpx.URL | None  # 代理 / 兼容 API
│   ├── websocket_base_url: str | httpx.URL | None
│   ├── timeout: float | Timeout | None | NotGiven
│   ├── max_retries: int = 2
│   ├── default_headers: Mapping[str, str] | None
│   ├── default_query: Mapping[str, object] | None
│   ├── http_client: httpx.Client | None  # 注入自定义 HTTP 客户端
│   ├── _strict_response_validation: bool = False
│   └── _enforce_credentials: bool = True
│
├── 🧬 继承链（3 层）
│   OpenAI → SyncAPIClient → BaseClient → Generic → object
│
├── 🌐 底层 HTTP 方法（来自 SyncAPIClient）
│   ├── .get(path, cast_to, options, stream, stream_cls)     → ResponseT
│   ├── .post(path, cast_to, body, content, options, files, stream) → ResponseT
│   ├── .put(path, cast_to, body, content, files, options)   → ResponseT
│   ├── .patch(path, cast_to, body, content, files, options) → ResponseT
│   ├── .delete(path, cast_to, body, content, options)       → ResponseT
│   ├── .request(cast_to, options, stream, stream_cls)       → ResponseT  # 底层通用请求
│   └── .get_api_list(path, model, page, body, options)      → SyncPageT # 分页
│
├── 🔧 辅助方法
│   ├── .with_options(**kwargs)        → Self  # 派生新 client，覆盖配置
│   ├── .with_raw_response             # 返回原始 HTTP 响应包装
│   ├── .with_streaming_response       # 返回流式响应包装
│   ├── .close()                       # 关闭底层 httpx 连接
│   └── .is_closed()                   → bool
│
│
│   ╔══════════════════════════════════════════════════════════╗
│   ║              核心资源树（cached_property）                 
│   ║      所有资源是懒加载的 —— 第一次访问时才实例化             
│   ╚══════════════════════════════════════════════════════════╝
│
├── 🧠 chat: Chat
│   └── completions: Completions
│       ├── .create(model, messages, temperature, ...)
│       │   → ChatCompletion
│       │   # 这是你 90% 时间用的那个方法
│       ├── .parse(model, messages, text_format, ...)
│       │   → ParsedChatCompletion[T]
│       │   # 结构化输出：直接返回 Pydantic 模型
│       ├── .stream(model, messages, ...)
│       │   → Stream[ChatCompletionChunk]
│       │   # SSE 流式响应
│       ├── .retrieve(completion_id) → ChatCompletion
│       ├── .update(completion_id, metadata)
│       ├── .delete(completion_id)
│       ├── .list(after, limit)       # 列出历史 completions
│       ├── .messages: Messages       # 已存储的消息
│       ├── .with_raw_response
│       └── .with_streaming_response
│
├── 📝 completions: Completions（旧版文本补全，Legacy）
│   └── .create(model, prompt, ...) → Completion
│
├── 🧬 embeddings: Embeddings
│   └── .create(input, model, dimensions, ...) → CreateEmbeddingResponse
│
├── 📁 files: Files
│   ├── .create(file, purpose, expires_after, ...)
│   ├── .list(after, limit)
│   ├── .retrieve(file_id)
│   ├── .retrieve_content(file_id)   # 下载文件内容
│   ├── .content(file_id)
│   ├── .delete(file_id)
│   └── .wait_for_processing(id, poll_interval, max_wait_seconds)
│
├── 🖼️ images: Images
│   ├── .generate(prompt, model, n, size, ...)
│   ├── .edit(image, prompt, mask, ...)
│   └── .create_variation(image, model, ...)
│
├── 🎛️ models: Models
│   ├── .list()
│   ├── .retrieve(model)
│   └── .delete(model)
│
├── 🛡️ moderations: Moderations
│   └── .create(input, model, ...)
│
├── 🎵 audio: Audio
│   ├── speech: Speech
│   │   └── .create(input, model, voice, speed, ...)  # TTS
│   ├── transcriptions: Transcriptions
│   │   └── .create(file, model, language, ...)       # Whisper
│   └── translations: Translations
│       └── .create(file, model, ...)                 # 翻译
│
├── 🔧 fine_tuning: FineTuning
│   ├── jobs: Jobs
│   │   ├── .create(model, training_file, ...)
│   │   ├── .list(after, limit)
│   │   ├── .retrieve(fine_tuning_job_id)
│   │   ├── .cancel(fine_tuning_job_id)
│   │   ├── .pause(fine_tuning_job_id)
│   │   ├── .resume(fine_tuning_job_id)
│   │   ├── .list_events(fine_tuning_job_id)
│   │   └── .checkpoints: Checkpoints
│   ├── checkpoints: Checkpoints
│   │   └── .permissions: Permissions
│   └── alpha: Alpha
│       └── .graders: Graders
│
├── 🧪 beta: Beta（实验性功能聚集地）
│   ├── assistants: Assistants
│   │   ├── .create(model, instructions, tools, ...)
│   │   ├── .list(after, before, limit, ...)
│   │   ├── .retrieve(assistant_id)
│   │   ├── .update(assistant_id, ...)
│   │   └── .delete(assistant_id)
│   ├── threads: Threads
│   │   ├── .create(messages, ...)
│   │   ├── .retrieve / .update / .delete
│   │   ├── .create_and_run(assistant_id, ...)
│   │   ├── .create_and_run_poll(...)
│   │   ├── .create_and_run_stream(...)
│   │   ├── .messages: Messages
│   │   └── .runs: Runs
│   ├── chat: Chat
│   │   └── completions: Completions（beta 频道的 chat）
│   ├── chatkit: ChatKit
│   │   ├── .sessions: Sessions
│   │   └── .threads: Threads
│   └── realtime: Realtime
│       ├── .connect(model, ...)         # WebSocket 连接
│       ├── .sessions: Sessions
│       └── .transcription_sessions: TranscriptionSessions
│
├── 📦 batches: Batches（异步批量处理）
│   ├── .create(completion_window, endpoint, input_file_id, ...)
│   ├── .list(after, limit)
│   ├── .retrieve(batch_id)
│   └── .cancel(batch_id)
│
├── 📤 uploads: Uploads（大文件分片上传）
│   ├── .create(bytes, filename, mime_type, purpose, ...)
│   ├── .complete(upload_id, part_ids, md5)
│   ├── .cancel(upload_id)
│   ├── .upload_file_chunked(file, mime_type, purpose, ...)
│   └── .parts: Parts
│       └── .create(upload_id, data, ...)
│
├── ⚡ realtime: Realtime
│   ├── .connect(call_id, model, ...)
│   ├── .calls: _Calls
│   └── .client_secrets: ClientSecrets
│
├── 💬 responses: Responses（新 Responses API）
│   ├── .create(input, model, tools, ...)
│   ├── .retrieve(response_id, include, ...)
│   ├── .delete(response_id)
│   ├── .cancel(response_id)
│   ├── .compact(model, ...)
│   ├── .parse(text_format, ...)     # 结构化解析
│   ├── .stream(response_id, input, ...)
│   ├── .connect(...)                # WebSocket
│   ├── .input_items: InputItems
│   └── .input_tokens: InputTokens
│
├── 🗄️ vector_stores: VectorStores
│   ├── .create(chunking_strategy, expires_after, ...)
│   ├── .list(after, before, limit, ...)
│   ├── .retrieve / .update / .delete
│   ├── .search(vector_store_id, query, filters, ...)
│   ├── .files: Files
│   └── .file_batches: FileBatches
│
├── 💬 conversations: Conversations
│   ├── .create(items, ...) / .retrieve / .update / .delete
│   └── .items: Items
│
├── 🧪 evals: Evals
│   ├── .create(data_source_config, testing_criteria, ...)
│   ├── .list / .retrieve / .update / .delete
│   └── .runs: Runs
│
├── 🏗️ admin: Admin
├── 📦 containers: Containers
├── 🧩 skills: Skills
├── 🎬 videos: Videos
└── 🪝 webhooks: Webhooks
```

---

<a id="toc-构造参数"></a>

## 构造参数：client

看了刚刚那颗**大树** 是不是觉得哈人？

我都说了，这颗树只是用来当参考的 ：）如果你好奇，就自己打开看看吧。但是，有些时候，你管不到这么多

client是一个“实例”，具体来讲，就是一个“遥控器”，填入相关参数之后，就可以完成相关的调用

通过改参数，就可以遥控不同的模型，很方便对吧

一个典型的client可以这么设置

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-...",         # 也可以是 Callable，需要时才求值
    organization="org-xxx",   # 多组织场景，给公司用的，个人开发着不用管
    project="proj-xxx",       # 项目隔离，这两个参数是给公司用的，主要是确保不同项目的互相分开，个人开发者不用管
    base_url="https://api.openai.com/v1",  # 代理 / 兼容 API（如 OneAPI）
    timeout=30.0,             # 可以是 float | httpx.Timeout | None 你的尝试时间，设置成114514.0 s 都无所谓
    max_retries=2,            # 自动重试次数，你可以按照自己的需求，来调整，比如我想让他多尝试几次，就把这个数值改大一点
    default_headers={"X-Custom": "value"}, # 自动附加的 HTTP 请求头,这个主要是调日志用的，没有特殊需求直接去掉
    default_query={"api-version": "2024-02-01"}, # 这个主要是，为了兼容性，比如有些平台很tmd混账，不按照规定格式来写，相当于相当于你告诉服务员：“不管我点啥，结账时都默认用‘会员88折’活动。” 这个没有特殊需求的时候直接去掉
    http_client=None,         # 注入自定义 httpx.Client，大部分时候直接去掉
)
```
哈哈，其实这里填写的都有点多了，其实，你这么写就可以了

```python
client = OpenAI(
    api_key="sk-114514",   # 推荐你的通过环境变量配置，也可直接写死（不推荐）
    base_url="https://api.deepseek.com")
)
```
我建议你购买国产模型的api,推荐 千问 和kimi 还有deepseek

关键细节：

- **`api_key` 可以是 `Callable[[], str]`** — 这意味着你可以传一个函数，每次请求时动态获取 key（比如从 Vault 读取临时凭证）。也可以是是你的环境变量。
- **`base_url`** — 换掉它就能对接任何 OpenAI 兼容 API（Ollama、vLLM、OneAPI、DeepSeek 等）。这是生态如此繁荣的核心原因。
- **`http_client`** — 直接注入 `httpx.Client` 实例，自定义连接池、代理、SSL 证书。
- **`max_retries`** — 默认 2 次。429 / 5xx 自动重试，指数退
- 避由 httpx 处理。


相关参数，比如重试时间啊，还有别的，看你的需求 感兴趣的话，就自己填就行了


<a id="toc-得到回复"></a>

## 得到回复

我们既然构造了client,尝试调用了

为此，我们可以这么写

```python
response = client.chat.completions.create(
    model="deepseek-v4-pro",      # 用的模型名，换了就能切别的模型（必填）
    messages=[                    # 对话内容，一个列表，装着每条消息
        {"role": "system", "content": "你是一个有用的助手"},
        #       ↑ 系统提示               ↑ 设定AI的人设/行为规则
        {"role": "user", "content": "你好啊，你能为我做什么"},
        #       ↑ 用户发言               ↑ 你实际想问的问题
    ],
    stream=False  # False=等AI写完一次性返回（简单省事）
                  # True=AI边写边往外蹦字（像打字机效果，下一篇细讲）
)    
```

接着 把ai的回复，可以打印出来

```python
print(response.choices[0].message.content)

print("                                            ") # 这几个空格只是分开用的，没啥意义 ：）
print("                                            ")
print("                                            ")

print(response)# print(response.choices[1].message.content)
```

我们会得到。类似这样的回答

```txt
你好！很高兴能帮到你！我可以在很多方面协助你，比如：

- **解答知识问题**：科学、历史、文化、技术……任何你好奇的领域，都能尽量给你解释清楚。
- **写作与润色**：帮你写文章、报告、邮件、故事，或者优化你现有的文字。
- **语言翻译**：多语言互译，或者帮你理解外文内容。
- **编程帮助**：解释代码、调试错误、提供算法思路等。
- **创意点子**：起名、策划活动、头脑风暴，交给我试试。
- **学习辅导**：帮你梳理知识点、总结重点、出题练习。
- **日常建议**：比如做菜、整理、时间管理等等。

有什么具体想让我帮忙的吗？直接说就行，我会尽力帮你搞定～
                                            
                                            
                                            
ChatCompletion(id='ba7ee2b2-a2bd-4e41-b526-bd2123a08fcf', choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='你好！很高兴能帮到你！我可以在很多方面协助你，比如：\n\n- **解答知识问题**：科学、历史、文化、技术……任何你好奇的领域，都能尽量给你解释清楚。\n- **写作与润色**：帮你写文章、报告、邮件、故事，或者优化你现有的文字。\n- **语言翻译**：多语言互译，或者帮你理解外文内容。\n- **编程帮助**：解释代码、调试错误、提供算法思路等。\n- **创意点子**：起名、策划活动、头脑风暴，交给我试试。\n- **学习辅导**：帮你梳理知识点、总结重点、出题练习。\n- **日常建议**：比如做菜、整理、时间管理等等。\n\n有什么具体想让我帮忙的吗？直接说就行，我会尽力帮你搞定～', refusal=None, role='assistant', annotations=None, audio=None, function_call=None, tool_calls=None, reasoning_content='我们需要理解用户的问题：“你好啊，你可以帮我做什么？” 这是一个友好的问候，并询问我能提供什么帮助。\n\n根据角色定义，我是一个有用的AI助手，协助用户解答问题。我应该友好地回应，列出我能提供的帮助，比如回答问题、解释概念、提供建议、帮忙写作、翻译、总结、编程帮助等等。还要鼓励用户具体说出需求。\n\n注意语气要热情、有帮助性。可以简短介绍自己，然后列举一些常见功能，最后邀请用户提出具体问题。\n\n由于是中文，用中文回复。'))], created=1779964322, model='deepseek-v4-pro', object='chat.completion', service_tier=None, system_fingerprint='fp_9954b31ca7_prod0820_fp8_kvcache_20260402', usage=CompletionUsage(completion_tokens=280, prompt_tokens=22, total_tokens=302, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=None, audio_tokens=None, reasoning_tokens=109, rejected_prediction_tokens=None), prompt_tokens_details=PromptTokensDetails(audio_tokens=None, cached_tokens=0), prompt_cache_hit_tokens=0, prompt_cache_miss_tokens=22))
```
你现在肯定很疑惑，为啥打印`response.choices[0].message.content` 可以得到一个回答，直接打印`response`，是这么一大串？

*注：这里的response是我们自己整的变量名，用来替代client.chat.completions.create(model="deepseek-v4-pro",messages=[{"role": "system", "content": "你是一个有用的助手"},{"role": "user", "content":"你好啊，你能为我做什么"},],stream=False)这么一大长串的，你用别的名字来命名也可以，把Response这个变量名字改成Homo,Mihoyo什么乱七八糟的都可以其实*

接下来，我将节选client这个结构树的其中的部分来讲解

<a id="toc-节选讲解"></a>

## 结合结构树的节选来讲解

<a id="toc-打印一大坨"></a>

### 为什么直接打印 response 是一大坨？

打印的这个 `response`，它不是一个字符串，它是一个 **对象**。

具体来说，它是一个 `ChatCompletion` 它想象成一份快递包裹：

- 真正想要的"回复内容"（`response.choices[0].message.content`）只是包裹里的一张纸条
- 而包裹上还贴着运单号、发货时间、重量、运费、签收状态……这些东西 Python 在 `print` 的时候一股脑全给你了

这就是为什么直接 `print(response)` 会看到 `id='ba7ee...'`、`model='deepseek-v4-pro'`、`usage=CompletionUsage(...)` 一大堆东西。

把这个分支单拎出来：

```txt
 chat: Chat
└── completions: Completions
    └── .create(model, messages, ...) → ChatCompletion
                                          │
                                          ├── id: str
                                          │   # 这次请求的唯一 ID，出问题找客服用的
                                          │
                                          ├── choices: list[Choice]
                                          │   └── Choice
                                          │       ├── index: int
                                          │       │   # choices 列表里的序号（你传 n=3 就会返回 3 个）
                                          │       ├── finish_reason: str
                                          │       │   # "stop"=正常结束 / "length"=被截断 / "tool_calls"=调用工具
                                          │       └── message: ChatCompletionMessage
                                          │              ├── role: str          # "assistant"
                                          │              ├── content: str | None # 要的回复
                                          │              ├── tool_calls: list | None
                                          │              └── reasoning_content: str | None
                                          │                   # DeepSeek 等推理模型的"思考过程"
                                          │
                                          ├── model: str
                                          │   # 实际使用的模型名
                                          │
                                          ├── usage: CompletionUsage
                                          │   ├── prompt_tokens: int       # 你的输入用了多少 token
                                          │   ├── completion_tokens: int   # AI 的回复用了多少 token
                                          │   ├── total_tokens: int        # 加起来一共多少
                                          │   └── reasoning_tokens: int    # 思考过程消耗的 token
                                          │
                                          └── created: int
                                              # Unix 时间戳，记录请求创建时间
```

<a id="toc-取值路径"></a>

### 讲解

```python
response.choices[0].message.content
#  ↑        ↑     ↑       ↑
# 包裹    第一份   消息    文本内容
#         回复
```

为什么是 `[0]`？因为一次请求可以要求返回多个回复（调 `n=` 参数），API 会把它们塞在 `choices` 列表里。只用一个，所以取 `[0]`。

你还可以用for循环，去打印多个回复
```python
from openai import OpenAI

client = OpenAI(
    api_key="your-api-key",                # 用环境变量，不要硬编码
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[
        {"role": "system", "content": "你是一个有用的AI助手。"},
        {"role": "user", "content": "讲一个短笑话"}
    ],
    n=3,          # 让模型一次生成 3 个不同的回复,想要多个回复的时候，必须在这里先约定好
    stream=False
)

# 用 for 循环逐个打印
for i, choice in enumerate(response.choices, start=1):
    print(f"--- 回复 {i} ---")
    print(choice.message.content)
    print()
```
对了，有些模型不支持n这个参数，比如deepseek,这个时候，循环三次就好了

```python

# 需要 3 条回复？循环 3 次
responses = []
for i in range(3):
    resp = client.chat.completions.create(
        model="deepseek-v4-pro",              # 注意！要用正确的模型名
        messages=[
            {"role": "system", "content": "你是一个有用的AI助手，协助用户解答问题。"},
            {"role": "user", "content": "你好啊，你可以帮我做什么？"},
        ],
        stream=False
    )
    responses.append(resp.choices[0].message.content)

# 打印所有回复
for idx, content in enumerate(responses, start=1):
    print(f"第{idx}条回复：")
    print(content)
    print("==="*20)

```

#### 参数

**1. `finish_reason` —— AI 为什么说完了？**

```python
print(response.choices[0].finish_reason)
# 通常输出 "stop"（正常结束）
```

它的取值只有几种：
- `"stop"` — 自然说完，或者命中了你设置的 `stop` 关键词
- `"length"` — token 超限被硬截断，话没说完（比如 `max_tokens` 设太小了）
- `"tool_calls"` — AI 觉得需要调工具，停止生成文本，改成给你函数调用参数

如果你想看 AI 是不是有话没说完，扫一眼这个就清楚了。

**2. `usage` —— 这次对话花了多少"Token"？**

```python
print(response.usage)
# CompletionUsage(
#     prompt_tokens=22,
#     completion_tokens=280,
#     total_tokens=302,
#     reasoning_tokens=109
# )
```

Token 差不多就是"AI 阅读/写作的字数单位"。`prompt_tokens` 是你输入的量，`completion_tokens` 是 AI 输出的量，`reasoning_tokens` 是推理模型（比如 DeepSeek-V4）的"内心独白"花了多少。各平台的计费就是用这些数字算出来的。

具体怎么计费各平台不一样，但**看 `usage` 字段，你就能算出每次调用的开销**。

**3. `reasoning_content` —— AI 在想什么？**

如果你用的是推理模型（DeepSeek-V4、o1 系列等），`message` 里还会多一个字段：

```python
print(response.choices[0].message.reasoning_content)
# 输出类似：
# "我们需要理解用户的问题：'你好啊，你可以帮我做什么？'
#  这是一个友好的问候，并询问我能提供什么帮助..."
```

这是 AI 在给出最终回复**之前**的思考过程。只有 DeepSeek、OpenAI o1/o3 等推理模型才会有。如果你用的是一般的对话模型（比如 gpt-4o、deepseek-chat），这个字段会是 `None`。

> 哦对了，**这些思考 token 也是要收费的**（在上面的 `usage.reasoning_tokens` 里可以看到），但它们默认不在聊天记录里存储 —— OpenAI 和 DeepSeek 的处理策略有点不一样，这个以后再说。
> 还有，梁圣人的恩情还不完，截至到我的写作时间（2026-05-28），deepseek-v4-pro永久打折了！永久1/4！
> \O/\O/\O/\O/

<a id="toc-回到树"></a>

### 回到那颗树

文章开头那棵大树画了 `chat`、`embeddings`、`images`、`audio`、`files`、`fine_tuning`、`batches`、`realtime` 等等一堆分支。

但刚开始的时候，90% 的时间只需要碰 `client.chat.completions.create` 这一个方法。它就是你跟 AI 对话的主入口。其他的：

- `images` → 生成图片，有些模型可以生图，但是我们亲爱的V4还没有
- `audio` → TTS 文字转语音 + Whisper 语音转文字
- `embeddings` → 把文字变成向量（做知识库、语义搜索才用得到）
- `files / uploads / vector_stores` → 文件上传和向量存储，给 RAG 准备的，我后面回讲
- `beta.assistants / beta.threads` → OpenAI 的"助手模式"，帮你自动管理上下文
- `realtime` → WebSocket 实时对话，延迟极低，做语音助手才用得着

**先整熟练 `chat`，别的分支有需要的时候再顺着树去摸**

---

好了，这篇就先到这里。下一篇我打算接着讲解 `messages` 怎么构造（system / user / assistant / tool 四个角色分别是干嘛的）、`temperature` / `top_p` 这些参数到底是啥，以及流式输出（`stream=True`）怎么处理。

回头见 ：）