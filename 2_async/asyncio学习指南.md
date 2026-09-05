# asyncio 学习指南（核心基础）

> 本指南聚焦 Python 标准库 `asyncio` 的**核心基础**：协程、`await`、Task、`gather`、`sleep`。
> 每个知识点都配有可独立运行的示例文件（位于本目录），文中的输出均为**实际运行结果**。

---

## 目录

1. [引言：为什么需要 asyncio](#1-引言为什么需要-asyncio)
2. [核心概念](#2-核心概念)
3. [核心函数](#3-核心函数)
4. [特性应用](#4-特性应用)
5. [注意事项](#5-注意事项)
6. [应用场景](#6-应用场景)
7. [时序例子](#7-时序例子)
8. [耗时对比](#8-耗时对比)
9. [总结与延伸](#9-总结与延伸)

---

## 1. 引言：为什么需要 asyncio

### 同步 vs 异步

程序里大量的时间并不是花在「计算」上，而是花在「等待」上——等网络响应、等数据库、等文件读写。传统的同步代码在等待时，线程就傻傻地卡住，什么都做不了：

```
同步（排队）：任务A ──等待──> 完成 ──> 任务B ──等待──> 完成 ──> 任务C ...
                       ↑ 这段时间 CPU 在空转
```

`asyncio` 的思路是：**当一个任务在等待时，立刻切换到另一个任务去执行**，从而让「等待」的时间被充分利用起来。

```
异步（并发）：任务A ──等待──┬─ 完成
            任务B ──等待──┤─ 完成
            任务C ──等待──┘─ 完成
            ↑ 三个任务同时进行，总耗时 ≈ 最慢的那一个
```

### IO 密集 vs CPU 密集

| 类型 | 例子 | asyncio 是否有效 |
|------|------|------------------|
| **IO 密集** | 爬虫、API 请求、数据库、文件、网络 | ✅ 非常适合，等待时间被复用 |
| **CPU 密集** | 大量计算、图像处理、加密 | ❌ 无效，`asyncio` 是单线程，计算不会变快 |

> 一句话：`asyncio` 解决的是「等得多」的问题，不是「算得多」的问题。

---

## 2. 核心概念

### 2.1 协程（coroutine）

用 `async def` 定义的函数叫**协程函数**。调用它**不会执行函数体**，而是返回一个**协程对象**：

```python
async def add(a, b):
    return a + b

coro = add(1, 2)   # 什么都不发生，只是拿到一个协程对象
```

> 这是初学者最容易踩的坑：**调用 `async def` 函数 ≠ 执行它**。详见第 5 节注意事项。

### 2.2 `await`

`await` 用来**等待一个协程执行完成**。它会让当前协程「暂停」，把控制权交还给事件循环，去运行别的任务：

```python
result = await add(1, 2)   # 只有 await 之后，协程才真正运行
```

### 2.3 可等待对象（awaitable）

`await` 后面只能跟「可等待对象」，常见的有三种：

- **协程对象**（coroutine object）—— 由 `async def` 函数调用产生
- **Task** —— 用 `asyncio.create_task()` 包装协程得到，代表一个「正在后台运行的协程」
- **Future** —— 更底层的占位对象，初学阶段很少直接用到

### 2.4 事件循环（event loop）

事件循环是 `asyncio` 的「调度器」。它维护一个任务队列，不断循环：

> 哪个协程就绪了，就运行它；运行到 `await` 时暂停它，切换到下一个就绪的协程。

**关键认知：`asyncio` 是单线程的。** 协程之间的切换是「协作式」的——只有碰到 `await` 才会让出控制权，不会像多线程那样被强制抢占。

---

## 3. 核心函数

### 3.1 `asyncio.run(coro)`

**整个程序的入口。** 接收一个协程，创建事件循环、运行它、结束后再关闭循环。一个程序通常只在 `main` 里调用一次。

```python
async def main():
    ...

asyncio.run(main())   # 顶层入口，只调用一次
```

> ⚠️ 不要在 `async` 函数**内部**调用 `asyncio.run()`（会报错）。`run` 是给「同步的世界」进入「异步的世界」用的入口。

### 3.2 `asyncio.sleep(seconds)`

**异步睡眠**。它和 `time.sleep()` 的关键区别在于：`asyncio.sleep` 会**让出控制权**，睡眠期间事件循环可以去跑别的协程；而 `time.sleep` 会把整个线程**阻塞住**。

```python
await asyncio.sleep(0.1)   # 让出 0.1 秒，期间别人可以跑
```

> `asyncio.sleep(0)` 是一个常用技巧：主动让出一次控制权，给其他任务一个运行机会。

### 3.3 `asyncio.create_task(coro)`

把协程包装成一个 **Task**，并**立即安排它并发运行**。返回的 Task 可以稍后再 `await` 取结果。

```python
task = asyncio.create_task(some_coro())
# 此刻任务已经在后台跑了，当前协程可以继续做别的事
result = await task   # 稍后再等待它的结果
```

### 3.4 `asyncio.gather(*aws)`

**并发运行多个可等待对象，并一次性收集它们的返回值**（按传入顺序返回一个列表）。这是最常用的并发工具。

```python
results = await asyncio.gather(
    fetch("A", 0.3),
    fetch("B", 0.1),
    fetch("C", 0.2),
)
# results == ["A 的结果", "B 的结果", "C 的结果"]
```

### 3.5 核心函数速览表

| 函数 | 作用 | 一句话记忆 |
|------|------|-----------|
| `asyncio.run(coro)` | 程序入口 | 启动事件循环跑顶层协程 |
| `async def` / `await` | 定义 / 等待协程 | 定义用 async，执行靠 await |
| `asyncio.sleep(s)` | 异步睡眠 | 让出控制权，不阻塞 |
| `asyncio.create_task(coro)` | 创建并发 Task | 立即在后台开跑 |
| `asyncio.gather(*aws)` | 并发 + 收集结果 | 并发跑一堆，按序拿结果 |

---

## 4. 特性应用

### 4.1 定义并运行一个协程

示例文件：[demo_coroutine.py](2_async/demo_coroutine.py)

```python
async def add(a: int, b: int) -> int:
    await asyncio.sleep(0)
    return a + b

async def main() -> None:
    coro = add(1, 2)        # 只创建协程对象，不执行
    result = await coro     # await 才真正执行
    print(result)

asyncio.run(main())
```

实际运行输出：

```
只调用不 await，得到的只是一个协程对象：
   <coroutine object add at 0x...>

await 之后：
  -> add(1, 2) 开始执行
  -> add(1, 2) 执行完毕
  结果 = 3
```

### 4.2 并发运行多个任务并收集结果

示例文件：[demo_task_gather.py](2_async/demo_task_gather.py)

```python
async def fetch(name: str, seconds: float) -> str:
    await asyncio.sleep(seconds)   # 模拟网络请求耗时
    return f"{name} 的结果"

# 方式一：gather 一行并发 + 收集
results = await asyncio.gather(fetch("A", 0.3), fetch("B", 0.1), fetch("C", 0.2))

# 方式二：create_task 先包装，再逐个 await
task_x = asyncio.create_task(fetch("X", 0.3))
task_y = asyncio.create_task(fetch("Y", 0.1))
result_x = await task_x
result_y = await task_y
```

实际运行输出（注意：三个任务**几乎同时开始**，总耗时 ≈ 最慢的 0.3s，而非三者之和 0.6s）：

```
  [67360.495] A 开始
  [67360.495] B 开始
  [67360.495] C 开始
  [67360.606] B 完成
  [67360.698] C 完成
  [67360.805] A 完成
gather 总耗时：0.311s
结果： ['A 的结果', 'B 的结果', 'C 的结果']
```

> 观察点：A/B/C 的「开始」时间戳几乎相同（都在 67360.495 附近），这就是**并发**的证据——不是 A 跑完才轮到 B。

### 4.3 收集返回值

`gather` 按**传入参数的顺序**返回结果列表（不是按完成顺序）。想要「谁先完成先处理谁」，那是进阶的 `asyncio.as_completed` 或 `asyncio.wait` 的活，本指南从略。

---

## 5. 注意事项

### 5.1 调用协程却忘了 `await` → 不会运行 + 警告

这是**最高频的坑**。看 [demo_warning.py](2_async/demo_warning.py) 的运行结果：

```
I:\...\demo_warning.py:19: RuntimeWarning: coroutine 'say_hi' was never awaited
  say_hi()
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
```

协程对象被创建后就被丢弃，函数体**一行都没执行**。修复方法：要么 `await` 它，要么交给 `create_task` / `gather`。

### 5.2 不要在协程里调用阻塞函数

`asyncio` 是**单线程**的。如果在协程里调用 `time.sleep()`、`requests.get()`、`open().read()` 这类阻塞操作，**整个事件循环会被卡死**，所有并发瞬间失效。

```python
# ❌ 错误：time.sleep 会阻塞整个事件循环
async def bad():
    time.sleep(1)          # 这 1 秒内，其他所有协程都无法运行

# ✅ 正确：用异步版本
async def good():
    await asyncio.sleep(1) # 让出控制权，其他协程照常运行
```

> 如果确实需要跑阻塞代码（比如老牌同步库），进阶可用 `asyncio.to_thread()` 丢到线程池，本指南从略。

### 5.3 `await` 只能用在 `async` 函数里

在普通函数里写 `await` 会直接报语法错误：

```python
def normal():
    await asyncio.sleep(1)   # SyntaxError
```

### 5.4 顶层入口只用一次 `asyncio.run`

`asyncio.run` 负责创建和关闭事件循环，程序里调用一次即可；嵌套调用会报 `RuntimeError`。

### 5.5 不是「并行」，是「并发」

`asyncio` 的协程在**同一个线程**里交替执行，不会真正同时运行两段 CPU 代码。因此：

- IO 密集任务 → 提速明显 ✅
- CPU 密集任务 → 不会变快，甚至更慢 ❌（该用多进程/多线程）

---

## 6. 应用场景

| 场景 | 说明 |
|------|------|
| **网络爬虫 / 并发请求** | 同时抓取大量网页，等待响应的空档复用给其他请求 |
| **并发调用 API** | 聚合多个后端接口，`gather` 一把梭 |
| **并发下载** | 多个文件同时下载，总耗时 ≈ 最大单个文件 |
| **异步数据库** | 配合异步驱动（如 `asyncpg`、`aiomysql`）做高并发查询 |
| **Web 服务** | FastAPI、Sanic 等框架底层就是 `asyncio` |
| **定时任务 / 心跳** | `asyncio.sleep` 实现不阻塞的周期任务 |

**不适用**：纯计算（数值仿真、视频编码等 CPU 密集），以及没有「等待」可复用的场景。

---

## 7. 时序例子

示例文件：[demo_timing_sequence.py](2_async/demo_timing_sequence.py)

两个 worker 协程「甲」「乙」，各执行 3 轮，每轮 `await asyncio.sleep(0.1)`。观察它们如何**交错执行**：

```
  [67361.296] 甲 第 0 轮开始
  [67361.296] 乙 第 0 轮开始      ← 甲让出后，乙立刻接手
  [67361.408] 甲 第 0 轮结束
  [67361.408] 甲 第 1 轮开始
  [67361.408] 乙 第 0 轮结束      ← 乙也同时醒来，继续交错
  [67361.408] 乙 第 1 轮开始
  [67361.518] 甲 第 1 轮结束
  [67361.518] 甲 第 2 轮开始
  [67361.518] 乙 第 1 轮结束
  [67361.518] 乙 第 2 轮开始
  [67361.626] 甲 第 2 轮结束
  [67361.626] 乙 第 2 轮结束
```

把它画成时间线：

```
甲:  [第0轮开始 ──sleep──> 第0轮结束][第1轮开始 ──sleep──> 第1轮结束][第2轮...]
乙:      [第0轮开始 ──sleep──> 第0轮结束][第1轮开始 ──sleep──> 第1轮结束]...
             ↑                        ↑
        甲在 sleep 让出控制权，乙趁机运行，两者交替前进
```

**核心结论**：每个协程都只在 `await` 处「停一下」，事件循环趁机切到别的协程，于是两者像两条并行的线一样交错推进——但背后始终只有一个线程在跑。

---

## 8. 耗时对比

示例文件：[demo_sync_vs_async.py](2_async/demo_sync_vs_async.py)

模拟 10 个请求，每个 0.1 秒：

```python
# 同步：time.sleep(0.1)，串行执行 10 次
# 异步：await asyncio.sleep(0.1)，gather 并发 10 个
```

实际运行输出：

```
同步版本总耗时：1.082s
异步版本总耗时：0.106s
```

**结果**：异步版约 **10 倍提速**（1.082s → 0.106s）。

这直观体现了第 1 节的结论：同步是「排队等」（总耗时 = 各任务耗时之和），异步是「一起等」（总耗时 ≈ 最慢的那一个）。任务越多、单个任务的等待时间越长，提速越明显。

---

## 9. 总结与延伸

### 核心要点回顾

1. `async def` 定义协程，**调用只是创建对象**，`await` 才真正执行。
2. 顶层用 `asyncio.run(main())` 启动，只调用一次。
3. 用 `asyncio.gather()` / `asyncio.create_task()` 实现并发。
4. 用 `asyncio.sleep()` 让出控制权，**绝不在协程里用 `time.sleep()` 等阻塞函数**。
5. `asyncio` 是**单线程并发**，擅长 IO 密集，不擅长 CPU 密集。

### 下一步进阶（本指南未展开）

- `asyncio.wait_for()` / `asyncio.timeout()` —— 超时控制
- `asyncio.wait()` / `asyncio.as_completed()` —— 更细粒度的并发管理（谁先完成先处理谁）
- `asyncio.shield()` 与任务取消 `task.cancel()` —— 取消与保护
- `asyncio.to_thread()` —— 把阻塞代码丢进线程池
- 同步原语（`Lock` / `Semaphore` / `Event`）、队列 `asyncio.Queue` —— 协程间的协调与限流

### 示例文件清单

| 文件 | 内容 |
|------|------|
| [demo_coroutine.py](2_async/demo_coroutine.py) | 协程、`await`、`asyncio.run` 基础 |
| [demo_warning.py](2_async/demo_warning.py) | 不 `await` 触发的 `RuntimeWarning` |
| [demo_task_gather.py](2_async/demo_task_gather.py) | `create_task` 与 `gather` 并发 |
| [demo_timing_sequence.py](2_async/demo_timing_sequence.py) | 时序例子：协程交错执行 |
| [demo_sync_vs_async.py](2_async/demo_sync_vs_async.py) | 耗时对比：同步 vs 异步 |
