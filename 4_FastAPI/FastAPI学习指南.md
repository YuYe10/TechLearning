# FastAPI 学习指南（进阶全面）

> 本指南系统讲解 **FastAPI** 的核心函数、特性应用、注意事项与应用场景。
> 每个知识点都配有可独立运行的示例文件（位于本目录），文中的输出均为**实际运行结果**。
> 环境：Python 3.10 · FastAPI 0.141 · Pydantic 2.13 · uvicorn 0.52。
>
> 建议先读 [2_async/asyncio学习指南.md](2_async/asyncio学习指南.md)：FastAPI 构建在 asyncio 之上，理解了协程与事件循环，才能看懂第 4.13 节和「时序例子」。

---

## 目录

1. [引言：为什么需要 FastAPI](#1-引言为什么需要-fastapi)
2. [快速开始](#2-快速开始)
3. [核心概念](#3-核心概念)
4. [核心函数与特性](#4-核心函数与特性)
5. [进阶特性应用](#5-进阶特性应用)
6. [注意事项](#6-注意事项)
7. [应用场景](#7-应用场景)
8. [时序例子](#8-时序例子)
9. [总结与延伸](#9-总结与延伸)
10. [示例文件清单](#10-示例文件清单)

---

## 1. 引言：为什么需要 FastAPI

FastAPI 是一个现代、高性能的 Python Web 框架，用于构建 API。它站在三个巨人肩上：

- **Starlette** —— 提供 HTTP/WebSocket 处理（异步 ASGI）
- **Pydantic** —— 提供数据校验与序列化
- **类型提示（type hints）** —— 用 Python 类型注解驱动一切

### 它的四大卖点

| 卖点 | 说明 |
|------|------|
| **快** | 基于异步 ASGI，性能对标 Node.js / Go |
| **少** | 代码量远少于 Flask/Django，写一个接口只要几行 |
| **自动文档** | 免费得到交互式文档 `/docs`（Swagger UI）和 `/openapi.json` |
| **类型驱动** | 类型注解自动做**参数校验、序列化、文档生成**，出错返回 422 |

### 与常见框架对比

| 框架 | 风格 | 特点 |
|------|------|------|
| Flask | 同步 WSGI | 轻量灵活，生态成熟，但无自动校验/文档 |
| Django | 同步全栈 | 自带 ORM/Admin/认证，功能全但偏重 |
| **FastAPI** | **异步 ASGI** | **类型驱动、自动文档、原生异步**，适合 API 服务 |

> 一句话：FastAPI 让你**用类型注解声明「接口长什么样」**，剩下的校验、文档、序列化它全包了。

---

## 2. 快速开始

### 2.1 安装

```bash
pip install fastapi "uvicorn[standard]"
# 进阶部分还用到：
pip install sqlalchemy pyjwt pytest python-multipart
```

### 2.2 最小应用

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
```

### 2.3 启动服务

```bash
uvicorn main:app --reload
# uvicorn <文件名>:<应用变量名>  --reload 表示代码改动自动重启
```

启动后访问：

- `http://127.0.0.1:8000/` —— 你的接口
- `http://127.0.0.1:8000/docs` —— **自动生成的交互式文档**（Swagger UI，可以直接在上面点按钮调接口）
- `http://127.0.0.1:8000/openapi.json` —— OpenAPI 规范（机器可读的接口描述）

> 本指南的示例文件为了「双击即可运行、无需手动起服务」，都用了 `TestClient` 直接调用接口。你上手写真实服务时，用上面的 `uvicorn` 命令即可。

---

## 3. 核心概念

### 3.1 ASGI 与 Uvicorn

- **WSGI**（Flask/Django 用）：同步标准，一个请求一个线程。
- **ASGI**（FastAPI 用）：异步标准，原生支持 `async/await` 和 WebSocket。

`uvicorn` 就是 ASGI 服务器，负责接收网络请求、跑你的 `app`。这也是为什么 FastAPI 能高效处理并发 IO。

### 3.2 Pydantic 模型

Pydantic 是数据校验库。你用 `BaseModel` 定义数据结构，FastAPI 会自动用它：

1. **解析**请求体（JSON → Python 对象）
2. **校验**类型与约束（不合规返回 422）
3. **序列化**响应（Python 对象 → JSON）

### 3.3 依赖注入（Depends）

「依赖注入」听着玄，其实就是：**把一个函数/对象「注入」到你的接口函数参数里**。好处是复用公共逻辑（鉴权、数据库会话、分页参数），且 FastAPI 会自动处理依赖的依赖（子依赖）。

### 3.4 OpenAPI 文档

你在每个接口上写的类型注解，会被 FastAPI 自动翻译成一份 OpenAPI 规范，从而免费得到交互式文档。**写代码即写文档**。

---

## 4. 核心函数与特性

> 每小节先讲用法，再给「实际运行输出」。完整可运行代码见对应的 `demo_*.py` 文件。

### 4.1 应用实例 `FastAPI()`

```python
app = FastAPI(title="我的应用", description="接口描述", version="0.1.0")
```

创建应用实例。`title` / `description` / `version` 会显示在 `/docs` 文档页上。

### 4.2 路由装饰器 `@app.get()` / `@app.post()` 等

```python
@app.get("/items")      # GET
@app.post("/items")     # POST
@app.put("/items/{id}") # PUT
@app.delete("/items/{id}")  # DELETE
```

每个装饰器对应一个 HTTP 方法，括号里是 URL 路径。`{id}` 是**路径参数**占位符。

### 4.3 路径参数

路径里的 `{user_id}` 作为函数参数传入，**类型会自动转换**：

```python
@app.get("/users/{user_id}")
def read_user(user_id: int):   # 声明为 int，FastAPI 自动把字符串转成 int
    return {"user_id": user_id}
```

### 4.4 查询参数

函数参数里**不是路径参数、且是简单类型**（str/int/bool 等）的，自动变成查询参数：

```python
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = "默认值", flag: bool = False):
    return {"item_id": item_id, "q": q, "flag": flag}
```

- 有默认值 → 可选参数；无默认值 → 必填参数
- `q: str | None = None` → 可选，不传为 `None`

示例文件：[demo_hello.py](3_FastAPI/demo_hello.py)

实际运行输出：

```
GET /                    -> {'message': 'Hello, FastAPI!'}
GET /users/42            -> {'user_id': 42, 'name': None}
GET /users/42?name=alice -> {'user_id': 42, 'name': 'alice'}
GET /items/7?q=hi&flag=t -> {'item_id': 7, 'q': 'hi', 'flag': True}
GET /users/abc           -> 状态码 422 | 错误: Input should be a valid integer, unable to parse string as an integer
```

> 观察点：`/users/abc` 里 `abc` 无法转成 int，FastAPI **自动返回 422**，这就是类型驱动的威力。

### 4.5 请求体（Pydantic `BaseModel`）

当参数是 Pydantic 模型时，FastAPI 自动从请求体（JSON）解析并校验：

```python
from pydantic import BaseModel, Field

class Item(BaseModel):
    name: str
    price: float = Field(gt=0)          # 校验：必须大于 0
    tags: list[str] = []
    email: str | None = None            # 可选字段

@app.post("/items/")
def create_item(item: Item):
    return item
```

### 4.6 响应模型 `response_model`

在装饰器里声明返回结构，FastAPI 会**过滤掉多余的字段**、做序列化、并写入文档：

```python
class ItemOut(BaseModel):
    name: str
    price: float

@app.post("/items/", response_model=ItemOut)
def create_item(item: Item):
    return item   # 即使 item 里有 tags/email，响应也只返回 name 和 price
```

示例文件：[demo_request_body.py](3_FastAPI/demo_request_body.py)

实际运行输出：

```
  收到请求体: {'name': '牙刷', 'price': 9.9, 'tags': ['日用'], 'email': 'a@b.com'}
正常请求 -> 200 {'name': '牙刷', 'price': 9.9}
price=-1  -> 状态码 422 | 错误: Input should be greater than 0
email 非法 -> 状态码 422 | 错误: value is not a valid email address: An email address must have an @-sign.
```

> 三个观察点：① `response_model` 把 `tags`/`email` 过滤掉了，只返回 `name` 和 `price`；② `price=-1` 违反 `gt=0` → 422；③ `email` 非法 → 422。校验**免费获得**。

### 4.7 依赖注入 `Depends`

四种常见用法，见 [demo_dependencies.py](3_FastAPI/demo_dependencies.py)：

```python
# 1) 函数依赖：抽取公共参数
def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
def read_items(commons: dict = Depends(common_parameters)):
    return commons

# 2) 类依赖：可带状态
class Pagination:
    def __init__(self, page: int = 1, size: int = 10):
        self.page, self.size = page, size

@app.get("/users/")
def list_users(p: Pagination = Depends(Pagination)):
    return {"page": p.page, "size": p.size}

# 3) 子依赖：依赖里还能依赖别的依赖
def get_current_user():
    return "alice"

def get_db(user: str = Depends(get_current_user)):
    return {"user": user, "conn": "数据库连接"}

# 4) yield 依赖：请求后清理（常用于关闭数据库会话）
def get_session():
    print("  [依赖] 打开数据库会话")
    try:
        yield "会话对象"
    finally:
        print("  [依赖] 关闭数据库会话")
```

实际运行输出：

```
函数依赖: {'q': 'hi', 'skip': 2, 'limit': 5}
类依赖:   {'page': 3, 'size': 20}
子依赖:   {'user': 'alice', 'conn': '数据库连接'}
  [依赖] 打开数据库会话
  [依赖] 关闭数据库会话
yield依赖: {'session': '会话对象'}
```

### 4.8 中间件与 CORS

**中间件**：在请求进入接口之前、响应返回之前执行，可做日志、耗时统计、鉴权等。见 [demo_middleware_cors.py](3_FastAPI/demo_middleware_cors.py)：

```python
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)      # 继续往下走
    response.headers["X-Process-Time"] = f"{(time.perf_counter()-start)*1000:.2f}ms"
    return response

# CORS：允许跨域（前后端分离时浏览器同源策略会拦截跨域请求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)
```

实际运行输出：

```
GET /        -> 200 {'message': 'hello'} | 耗时头: 3.45ms
GET /items/0 -> 404 {'detail': 'item not found'}
GET /boom    -> 400 {'error': '这是自定义的 ValueError'}
带 Origin 头 -> CORS 响应头: *
```

### 4.9 异常处理

```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id == 0:
        raise HTTPException(status_code=404, detail="item not found")
    return {"item_id": item_id}

# 自定义异常处理器：统一返回结构化错误
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(status_code=400, content={"error": str(exc)})
```

### 4.10 后台任务 `BackgroundTasks`

把慢操作（发邮件、写日志）丢到后台，接口**先返回响应**。见 [demo_background_tasks.py](3_FastAPI/demo_background_tasks.py)：

```python
@app.post("/users/")
def create_user(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, email, "欢迎注册！")
    return {"status": "用户已创建", "email": email}
```

实际运行输出：

```
  [后台任务] 已向 a@b.com 发送：欢迎注册！
{'status': '用户已创建', 'email': 'a@b.com'}
（真实服务里，客户端在后台任务完成前就已拿到响应；TestClient 会等后台任务跑完）
```

### 4.11 表单 `Form` 与文件 `File`

```python
from fastapi import Form, File, UploadFile

@app.post("/login/")
def login(username: str = Form(), password: str = Form()):
    return {"username": username}

@app.post("/upload/")
async def upload(file: UploadFile = File()):
    content = await file.read()   # 读取文件内容
    return {"filename": file.filename, "size": len(content)}
```

实际运行输出（见 [demo_forms_files.py](3_FastAPI/demo_forms_files.py)）：

```
表单登录 -> {'username': 'alice'}
文件上传 -> {'filename': 'hello.txt', 'size': 13}
```

### 4.12 表单/文件与请求体的区分规则

FastAPI 靠**参数类型**判断参数从哪来，这是理解接口行为的关键：

| 参数类型 | 来源 |
|----------|------|
| 路径 `{id}` | 路径参数 |
| 简单类型 `str`/`int`/`bool` | 查询参数 |
| `BaseModel` 子类 | 请求体（JSON） |
| `Form()` / `File()` | 表单 / 文件 |

### 4.13 `async def` vs `def`（关键！）

这是 FastAPI 最重要的一个区分：

- **`def`（同步函数）**：FastAPI 会把它丢进**线程池**运行，所以函数里可以放心写阻塞代码（`time.sleep`、`requests`、同步数据库）。
- **`async def`（异步函数）**：直接在**事件循环**上运行，函数里**绝不能**写阻塞代码，否则整个事件循环被卡死，所有请求都动不了。

```python
@app.get("/a")            # ✅ 同步：阻塞调用会进线程池，不卡事件循环
def sync_route():
    time.sleep(1)
    return {"msg": "ok"}

@app.get("/b")            # ✅ 异步：用异步库，正确让出控制权
async def async_route():
    await asyncio.sleep(1)
    return {"msg": "ok"}

@app.get("/c")            # ❌ 异步函数里写阻塞调用 → 卡死整个事件循环！
async def bad_route():
    time.sleep(1)
    return {"msg": "ok"}
```

> 经验法则：接口里用的是**异步库**（httpx、asyncpg、aiosqlite）→ 用 `async def`；用的是**同步库**（requests、SQLAlchemy 同步版）→ 用 `def`。**最忌讳 `async def` 里夹 `time.sleep` 这类阻塞调用**，第 8 节「时序例子」用真实数据展示了后果。

---

## 5. 进阶特性应用

### 5.1 数据库（SQLAlchemy + SQLite）

用 SQLAlchemy 2.0 + SQLite 做一套完整的 CRUD，并用 `Depends` 管理数据库会话。见 [demo_database.py](3_FastAPI/demo_database.py)。

关键套路：

```python
def get_db():
    db = SessionLocal()
    try:
        yield db                 # 请求前：提供会话
    finally:
        db.close()               # 请求后：关闭会话

class ItemOut(ItemCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)   # Pydantic v2：允许从 ORM 对象读取

@app.post("/items/", response_model=ItemOut)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = Item(name=item.name, price=item.price)
    db.add(db_item); db.commit(); db.refresh(db_item)
    return db_item
```

实际运行输出：

```
新增: {'name': '苹果', 'price': 3.5, 'id': 1}
新增: {'name': '香蕉', 'price': 2.0, 'id': 2}
列表: [{'name': '苹果', 'price': 3.5, 'id': 1}, {'name': '香蕉', 'price': 2.0, 'id': 2}]
单个: {'name': '苹果', 'price': 3.5, 'id': 1}
查不存在 -> 状态码 404 | {'detail': '未找到该商品'}
```

### 5.2 认证（JWT）

登录发 token，受保护接口用 `Depends` 校验 token。见 [demo_auth_jwt.py](3_FastAPI/demo_auth_jwt.py)。

```python
@app.post("/login/")
def login(username: str):
    return {"access_token": create_token(username), "token_type": "bearer"}

@app.get("/me/")
def me(username: str = Depends(get_current_user)):   # 校验通过才拿到 username
    return {"username": username}
```

实际运行输出：

```
登录拿到 token: eyJhbGciOiJIUzI1NiIsInR5cCI6Ik...
不带 token -> 状态码 401 | {'detail': '缺少 token'}
带 token   -> 200 {'username': 'alice'}
过期 token -> 状态码 401 | {'detail': 'token 已过期'}
```

### 5.3 WebSocket

FastAPI 原生支持 WebSocket 双向通信。见 [demo_websocket.py](3_FastAPI/demo_websocket.py)：

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"回显: {data}")
    except WebSocketDisconnect:
        print("客户端已断开")
```

实际运行输出：

```
回显: 你好
回显: fastapi
  客户端已断开
```

### 5.4 测试（pytest + TestClient）

FastAPI 提供 `TestClient`（基于 httpx），配合 pytest 直接测试接口。见 [demo_test.py](3_FastAPI/demo_test.py)：

```python
client = TestClient(app)

def test_add():
    assert client.get("/add/1/2").json() == {"result": 3}

def test_add_type_error():
    assert client.get("/add/a/b").status_code == 422
```

运行 `pytest demo_test.py -v` 实际输出：

```
demo_test.py::test_add PASSED                                            [ 50%]
demo_test.py::test_add_type_error PASSED                                 [100%]
============================== 2 passed in 0.40s ==============================
```

---

## 6. 注意事项

### 6.1 `async def` 路由里禁止阻塞调用（最高频的坑）

`async def` 函数直接跑在事件循环上，一旦里面调用 `time.sleep`、`requests.get`、同步数据库查询，**整个服务会被卡死**，其他请求全部排队。详见第 8 节「时序例子」。

```python
# ❌ 错误：async 路由里用阻塞函数，一个慢请求拖垮所有请求
# ✅ 正确：改用 await 异步版本，或把接口改成 def（自动进线程池）
```

### 6.2 `def` 路由会自动进线程池

与 6.1 相反：`def` 路由由 FastAPI 放到线程池执行，所以**同步阻塞代码写在 `def` 里是安全的**。别误以为「所有接口都要 async」。

### 6.3 路径参数顺序：固定路径要在动态路径之前

```python
@app.get("/users/me")        # ✅ 先声明固定路径
def read_me(): ...

@app.get("/users/{user_id}") # 后声明动态路径
def read_user(user_id: int): ...
```

如果反过来，`/users/me` 会被 `/users/{user_id}` 抢先匹配，`user_id` 得到 `"me"`（还会触发 int 转换失败）。

### 6.4 记得声明返回类型

接口最好写**返回类型注解**（或 `response_model`），否则 FastAPI 无法自动生成完整的响应文档，返回的 Pydantic 对象也不会被正确序列化。

```python
@app.get("/users/{id}", response_model=UserOut)   # ✅ 声明返回结构
def get_user(id: int): ...
```

### 6.5 Pydantic v2 与 v1 的差异

网上很多教程是 Pydantic v1 的写法，v2 已不兼容。常见差异：

| 操作 | v1（旧） | v2（新） |
|------|----------|----------|
| 读取模型字段为字典 | `item.dict()` | `item.model_dump()` |
| 从 ORM 对象读取 | `class Config: orm_mode = True` | `model_config = ConfigDict(from_attributes=True)` |

### 6.6 请求体 vs 查询参数别搞混

记住 4.12 的规则：简单类型是查询参数，`BaseModel` 才是请求体。如果你想在一个接口里**同时**收查询参数和 JSON 请求体，需要用 `Body()` 显式声明：

```python
from fastapi import Body
@app.put("/items/{id}")
def update(id: int, item: Item, q: str = Body("")):  # 显式声明 q 在请求体里
    ...
```

### 6.7 `response_model` 会过滤字段

`response_model` 声明了哪些字段，响应就**只返回哪些字段**——多出来的会被静默丢弃。这既是优点（隐藏敏感字段），也是坑（字段忘了声明就返回不出来）。

### 6.8 TestClient 与真实服务器的差异

`TestClient` 会**同步等待后台任务完成**，而真实 uvicorn 服务里后台任务在响应之后异步执行。所以「后台任务是否阻塞客户端」这个特性，用 TestClient 看不出来，要起真实服务器验证（本指南第 4.10 节已注明）。

### 6.9 CORS 别乱配 `allow_origins=["*"]`

跨域只在前端需要时才开。若同时配了 `allow_origins=["*"]` 和 `allow_credentials=True`，是不允许的组合，会导致鉴权 Cookie 失效。生产环境应把 `*` 改成具体的域名白名单。

### 6.10 JWT 密钥要够长、用环境变量

HS256 算法要求密钥至少 32 字节（太短会告警 `InsecureKeyLengthWarning`）。密钥绝不能硬编码在代码里，要用环境变量或配置中心管理。

### 6.11 Windows 控制台中文乱码

在 Windows 命令行直接 `python demo_xxx.py`，若中文输出乱码，是因为默认用 GBK 编码。加上环境变量即可：

```bash
PYTHONUTF8=1 python demo_hello.py
```

### 6.12 版本提示：Starlette 弃用告警

较新的 Starlette 版本用 `TestClient` 时会提示 `Using httpx with starlette.testclient is deprecated`，这**只是弃用提示，不影响运行**，忽略即可。

---

## 7. 应用场景

| 场景 | 说明 |
|------|------|
| **RESTful API / 微服务** | 类型驱动 + 自动文档，是 FastAPI 的主场 |
| **机器学习 / 推理服务** | 加载模型后暴露 `/predict` 接口，自动文档方便联调 |
| **前后端分离的后端** | 配 CORS，输出 JSON，供 Vue/React 调用 |
| **内部工具 / 管理后台 API** | 几行代码暴露一个接口，自动生成 Swagger 文档 |
| **数据校验网关** | 用 Pydantic 做入参校验，天然返回 422 |
| **实时通信** | WebSocket 实现聊天、推送、实时日志 |
| **BFF（后端聚合层）** | 聚合多个内部接口，配合 asyncio 并发请求提速 |

**不适用**：传统服务端渲染的整站（用 Django 更省心）、纯 CPU 密集计算（FastAPI 本身不解决计算问题，仍要走线程池/进程池）。

---

## 8. 时序例子

示例文件：[demo_timing_async.py](3_FastAPI/demo_timing_async.py)

两个 `async def` 路由，都「睡」0.1 秒，区别是：

- `/blocking` —— `time.sleep(0.1)`（阻塞，卡死事件循环）
- `/nonblocking` —— `await asyncio.sleep(0.1)`（让出控制权）

用真实 uvicorn 服务器 + 10 个并发请求，测量总耗时：

```python
@app.get("/blocking")
async def blocking():
    time.sleep(0.1)          # ❌ 阻塞 → 请求串行排队
    return {"msg": "ok"}

@app.get("/nonblocking")
async def nonblocking():
    await asyncio.sleep(0.1) # ✅ 让出 → 请求并发执行
    return {"msg": "ok"}
```

实际运行输出：

```
10 个并发请求 /blocking    (async 路由里用 time.sleep)     总耗时 1.144s
10 个并发请求 /nonblocking (async 路由里 await asyncio.sleep) 总耗时 0.178s
```

把它画成时间线：

```
/blocking    请求1 ──sleep(卡死)──> 请求2 ──sleep──> ... 请求10
             ↑ 一次只能处理一个，10 个串行 = 1.0s + 开销

/nonblocking 请求1 ──await sleep──┬─ 完成
             请求2 ──await sleep──┤─ 完成
             请求3 ──await sleep──┘─ 完成
             ↑ 10 个并发，总耗时 ≈ 最慢的一个 = 0.1s + 开销
```

**核心结论**：在 `async def` 路由里，`time.sleep` 让整个服务「卡住」，10 个请求只能排队串行（≈1.14s）；换成 `await asyncio.sleep` 后 10 个请求并发执行（≈0.18s），**约 6 倍提速**。这正是 [2_async](2_async) 里「协程里不能用阻塞函数」在 FastAPI 中的直接体现。

> 如果实在要跑阻塞代码（老牌同步库），把接口声明为 `def`，FastAPI 会自动丢进线程池，同样不会卡事件循环。

---

## 9. 总结与延伸

### 核心要点回顾

1. **类型驱动**：用类型注解声明参数和返回，FastAPI 自动做校验、序列化、文档。
2. **路由**：`@app.get/post/...` 定义接口，`{id}` 是路径参数，简单类型是查询参数，`BaseModel` 是请求体。
3. **Pydantic**：`BaseModel` 定义数据结构，`Field(gt=0)` 加约束，`response_model` 控制返回。
4. **依赖注入**：`Depends` 复用逻辑（鉴权、数据库会话、分页），支持子依赖和 `yield` 清理。
5. **异步**：`async def` 里只写 `await` 异步代码，阻塞代码放 `def`（进线程池）或 `asyncio.to_thread`。
6. **自动文档**：`/docs` 交互式文档、`/openapi.json` 规范，免费获得。
7. **周边**：中间件/CORS、异常处理、后台任务、表单/文件、WebSocket、测试——都是开箱即用。

### 下一步延伸（本指南未展开）

- **SQLModel** —— FastAPI 作者 tiangolo 出的 ORM，融合 SQLAlchemy + Pydantic，写起来更顺
- **`pydantic-settings`** —— 用 `.env` / 环境变量管理配置
- **异步数据库** —— `asyncpg`（PostgreSQL）、`aiosqlite` 配合 `async def` 路由
- **后台任务队列** —— 重量级任务用 Celery / ARQ 代替 `BackgroundTasks`
- **限流与鉴权进阶** —— 中间件实现限流、OAuth2 / 第三方登录
- **生产部署** —— `gunicorn -k uvicorn.workers.UvicornWorker` 多进程、Docker、反向代理（Nginx）
- **结构化项目** —— 拆分 `routers/` `models/` `schemas/` `deps/` 目录

### 示例文件清单

| 文件 | 内容 |
|------|------|
| [demo_hello.py](3_FastAPI/demo_hello.py) | 最小应用、路由、路径/查询参数、422 校验 |
| [demo_request_body.py](3_FastAPI/demo_request_body.py) | Pydantic 请求体、字段校验、response_model |
| [demo_dependencies.py](3_FastAPI/demo_dependencies.py) | Depends 四种用法：函数/类/子依赖/yield |
| [demo_middleware_cors.py](3_FastAPI/demo_middleware_cors.py) | 中间件、CORS、HTTPException、自定义异常 |
| [demo_background_tasks.py](3_FastAPI/demo_background_tasks.py) | 后台任务 BackgroundTasks |
| [demo_forms_files.py](3_FastAPI/demo_forms_files.py) | 表单 Form 与文件 UploadFile |
| [demo_database.py](3_FastAPI/demo_database.py) | SQLAlchemy + SQLite CRUD |
| [demo_auth_jwt.py](3_FastAPI/demo_auth_jwt.py) | JWT 认证流程 |
| [demo_websocket.py](3_FastAPI/demo_websocket.py) | WebSocket 双向通信 |
| [demo_test.py](3_FastAPI/demo_test.py) | pytest + TestClient 测试 |
| [demo_timing_async.py](3_FastAPI/demo_timing_async.py) | 时序例子：async 路由阻塞 vs 非阻塞 |
