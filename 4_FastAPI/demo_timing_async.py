"""时序例子：async 路由里的阻塞调用会卡死整个事件循环。

用真实 uvicorn 服务器 + 10 个并发请求，对比：
  /blocking    —— async def 路由里用 time.sleep()（阻塞）→ 串行，慢
  /nonblocking —— async def 路由里用 await asyncio.sleep()（让出）→ 并发，快
"""
import asyncio
import threading
import time

import httpx
import uvicorn
from fastapi import FastAPI

app = FastAPI()
PORT = 8123


@app.get("/blocking")
async def blocking():
    time.sleep(0.1)  # ❌ 在 async 路由里阻塞：整个事件循环被卡住
    return {"msg": "ok"}


@app.get("/nonblocking")
async def nonblocking():
    await asyncio.sleep(0.1)  # ✅ 让出控制权，其他请求可以继续
    return {"msg": "ok"}


def run_server():
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")


async def fire(path: str, n: int) -> float:
    async with httpx.AsyncClient() as client:
        t0 = time.perf_counter()
        await asyncio.gather(*[client.get(f"http://127.0.0.1:{PORT}{path}") for _ in range(n)])
        return time.perf_counter() - t0


if __name__ == "__main__":
    server = threading.Thread(target=run_server, daemon=True)
    server.start()
    # 等待服务器就绪
    for _ in range(100):
        try:
            httpx.get(f"http://127.0.0.1:{PORT}/openapi.json")
            break
        except Exception:
            time.sleep(0.1)

    N = 10
    t_block = asyncio.run(fire("/blocking", N))
    t_nonblock = asyncio.run(fire("/nonblocking", N))
    print(f"{N} 个并发请求 /blocking    (async 路由里用 time.sleep)     总耗时 {t_block:.3f}s")
    print(f"{N} 个并发请求 /nonblocking (async 路由里 await asyncio.sleep) 总耗时 {t_nonblock:.3f}s")
