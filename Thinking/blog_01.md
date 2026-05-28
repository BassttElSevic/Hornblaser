# 庖丁解牛：用一棵树彻底搞懂 OpenAI Python Client

> 基于 `openai` v2.38.0 源码反向分析，非猜测、非文档复制。

---

## 为什么写这篇

用 `openai` 库大半年了，一直是 `client.chat.completions.create()` 一把梭。直到某天想看一个 completion 的原始 HTTP 响应头，才发现自己根本不知道 `with_raw_response` 是什么、放在哪个层级、背后的 `httpx` 做了多少事。

这篇是我把整个 client 拆开后的笔记。一棵树，从根到叶。

---

## 全景树

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
│   ║              核心资源树（cached_property）                 ║
│   ║      所有资源是懒加载的 —— 第一次访问时才实例化              ║
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

## 一、构造参数：client 的"基因"

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-...",         # 也可以是 Callable，需要时才求值
    organization="org-xxx",   # 多组织场景
    project="proj-xxx",       # 项目隔离
    base_url="https://api.openai.com/v1",  # 代理 / 兼容 API（如 OneAPI）
    timeout=30.0,             # 可以是 float | httpx.Timeout | None
    max_retries=2,            # 自动重试次数
    default_headers={"X-Custom": "value"},
    default_query={"api-version": "2024-02-01"},
    http_client=None,         # 注入自定义 httpx.Client
)
```

关键细节：

- **`api_key` 可以是 `Callable[[], str]`** — 这意味着你可以传一个函数，每次请求时动态获取 key（比如从 Vault 读取临时凭证）。
- **`base_url`** — 换掉它就能对接任何 OpenAI 兼容 API（Ollama、vLLM、OneAPI、DeepSeek 等）。这是生态如此繁荣的核心原因。
- **`http_client`** — 直接注入 `httpx.Client` 实例，自定义连接池、代理、SSL 证书。
- **`max_retries`** — 默认 2 次。429 / 5xx 自动重试，指数退避由 httpx 处理。

---

## 二、继承链：3 层抽象

```
OpenAI
 └── SyncAPIClient    ← 提供 get/post/put/patch/delete/request
      └── BaseClient  ← 管理 httpx 客户端、认证、重试
```

`SyncAPIClient` 提供了 7 个 HTTP 方法：`get`, `post`, `put`, `patch`, `delete`, `request`（通用）, `get_api_list`（自动分页）。所有资源方法最终都落到这几个方法上。

**这意味着你可以绕过高层封装直接发请求：**

```python
# 直接调用底层 HTTP 方法
resp = client.post(
    "/chat/completions",
    body={
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": "hi"}]
    },
    cast_to=dict,  # 类型转换目标
)
```

---

## 三、资源类的工作原理

每个资源（`chat`, `files`, `models` 等）在 client 上都是 **`cached_property`**：

```python
class OpenAI(SyncAPIClient):
    @cached_property
    def chat(self) -> Chat:
        return Chat(self)  # 传入 client 自身
```

这意味着：
1. **懒加载** — 只有你第一次访问 `client.chat` 时才实例化。
2. **单例** — 同一个 client 实例的 `chat` 永远是同一个对象。
3. **资源持有 client 引用** — 所有 `Chat`, `Completions` 等资源继承自 `SyncAPIResource`，内部持有 `self._client`，所以能直接发 HTTP 请求。

```
SyncAPIResource
 ├── self._client: OpenAI    ← 回到 client，调用 .post() / .get()
 └── def create(...):          ← 拼装 body → self._client.post(...)
```

---

## 四、一次请求的完整调用链

以 `client.chat.completions.create(model="gpt-4o", messages=[...])` 为例：

```
1. client.chat                          # cached_property → Chat(client)
2.       .completions                   # cached_property → Completions(chat._client)
3.                .create(model, msgs)  # 拼装 body, cast_to=ChatCompletion
4.    → self._client.post(              # SyncAPIClient.post()
         path="/chat/completions",
         body={...},
         cast_to=ChatCompletion,         # pydantic 模型
         stream=False,
       )
5.      → self._client.request(         # BaseClient.request()
           method="POST",
           url="https://api.openai.com/v1/chat/completions",
           headers={"Authorization": "Bearer sk-..."},
           content=json.dumps(body),
         )
6.        → httpx.Client.send(          # 实际 HTTP 请求
             Request(method="POST", url=..., headers=..., content=...)
           )
7.        ← httpx.Response(status=200, ...)
8.      ← APIResponse(raw=response, cast_to=ChatCompletion)
9.    ← ChatCompletion(id="chatcmpl-...", choices=[...], ...)
```

每一步都有明确的职责边界：
- **Resource 层**（Completions）负责拼请求体、选路由
- **SyncAPIClient 层**（post）负责拼完整 URL、处理 cast_to
- **BaseClient 层**（request）负责认证头、重试、错误处理
- **httpx 层**负责真正的网络 I/O

---

## 五、`with_raw_response` 和 `with_streaming_response`

这是最容易迷惑的两个属性。它们不是方法，而是返回一个**代理对象**。

### `with_raw_response`

```python
# 正常调用：返回 ChatCompletion 对象
completion = client.chat.completions.create(model="gpt-4o", messages=[...])
type(completion)  # <class 'openai.types.chat.ChatCompletion'>

# 获取原始响应（含 HTTP 状态码、响应头）
raw = client.chat.completions.with_raw_response.create(model="gpt-4o", messages=[...])
type(raw)  # <class 'openai._response.APIResponse[ChatCompletion]'>
raw.status_code        # 200
raw.headers            # httpx.Headers
raw.parse()            # ChatCompletion（等同于正常调用的返回值）
raw.http_response      # httpx.Response 原始对象
```

### `with_streaming_response`

```python
stream_resp = client.chat.completions.with_streaming_response.create(
    model="gpt-4o", messages=[...], stream=True
)
type(stream_resp)  # <class 'openai._streaming.Stream[ChatCompletionChunk]'>
stream_resp.headers       # 响应头
stream_resp.status_code   # 200

for chunk in stream_resp:
    print(chunk.choices[0].delta.content)
```

**位置规则：** `with_raw_response` 和 `with_streaming_response` 放在你要拦截的**资源层级**上。放在 `client.with_raw_response.chat.completions.create()` 会拦截所有 chat 请求；放在 `client.chat.completions.with_raw_response.create()` 只拦截 completions 的请求。

---

## 六、`with_options`：派生新 client

```python
# 不改原 client，派生一个超时不同的新 client
fast_client = client.with_options(timeout=5.0)

# 派生一个指向不同 base_url 的 client（方便同时调多个 API）
deepseek_client = client.with_options(
    base_url="https://api.deepseek.com/v1",
    api_key="sk-deepseek-...",
)
```

内部实现是创建一个新的 `OpenAI` 实例，复制原有配置并覆盖指定字段。原 client 完全不受影响。

---

## 七、`Omit` 与 `NOT_GIVEN`：API 层面的"不传"语义

openai 库为此专门设计了两个哨兵值：

- **`NOT_GIVEN`**（`NotGiven` 类型）：这个参数用户没有传。
- **`Omit`**（`Omit` 类型）：这个字段在请求体里**不出现**。

Python 的 `None` 在 API 语义里是有意义的（比如 `temperature=None` 让模型用默认值），而 `Omit` 才是真正的"别把这个字段放进 JSON"。

```python
from openai import NOT_GIVEN

# 下面两个请求发的 JSON 不同：
client.chat.completions.create(model="gpt-4o", messages=[...], temperature=None)
# → {"model": "gpt-4o", "messages": [...], "temperature": null}

client.chat.completions.create(model="gpt-4o", messages=[...])
# → {"model": "gpt-4o", "messages": [...]}  ← 没有 temperature 字段
```

这个设计让 Python 端能精确映射 OpenAI API 的"可选但传了 null"和"完全不传"两种语义。

---

## 八、关键设计决策一览

| 设计点 | 实现 | 好处 |
|--------|------|------|
| 资源层级 | `cached_property` 懒加载 | 不访问的资源不实例化，省内存 |
| HTTP 传输 | `httpx` | 连接池、HTTP/2、自动重试、代理 |
| 类型安全 | Pydantic 模型 (`cast_to`) | 响应自动校验 + 反序列化 |
| 哨兵值 | `NOT_GIVEN` / `Omit` | None 和"不传"有不同语义 |
| 流式 | SSE → `Stream[T]` 迭代器 | 统一接口，背后是生成器 |
| 原始响应 | `with_raw_response` 代理 | 不改 API 签名，无侵入 |
| 配置派生 | `with_options()` | 不改原 client，多端点共存 |

---

## 九、总结：一张心智模型图

```
       ┌──────────────────────────────────────┐
       │           OpenAI(client)             │
       │  api_key, base_url, timeout, httpx   │
       └────┬─────┬─────┬─────┬─────┬────────┘
            │     │     │     │     │
         chat  files audio  ...  beta      ← 资源层 (cached_property)
            │     │     │     │     │
       completions  ...                ← 子资源层
            │
         .create()                      ← 拼 body → cast_to
            │
       SyncAPIClient.post()             ← 拼 URL → request
            │
       BaseClient.request()             ← 认证头、重试
            │
       httpx.Client.send()              ← 网络 I/O
            │
       APIResponse / Stream[T]          ← 反序列化
            │
       ChatCompletion / dict / ...      ← 你的数据
```

从上到下是**请求**路径，从下到上是**响应**路径。每一层只做一件事，换掉任何一层都不会影响其他层。

这就是 `openai` client 的全貌。不是黑箱，是一组清晰的俄罗斯套娃。

---

> 下一篇计划：深入 `httpx` 层，看看连接池、重试策略、流式 SSE 解析到底是怎么工作的。
