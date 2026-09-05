"""耗时对比：同步 vs 异步

场景：模拟 10 个网络请求，每个耗时 0.1 秒。
- 同步版本：一个一个做，总耗时 ≈ 10 × 0.1 = 1.0 秒
- 异步版本：并发做，总耗时 ≈ 0.1 秒（取决于最慢的那一个）
"""

import asyncio
import time


# ---------- 同步版本 ----------
def sync_request(i: int) -> None:
    time.sleep(0.1)   # 阻塞 0.1 秒，模拟同步网络请求


def sync_main() -> None:
    t0 = time.perf_counter()
    for i in range(10):
        sync_request(i)
    print(f"同步版本总耗时：{time.perf_counter() - t0:.3f}s")


# ---------- 异步版本 ----------
async def async_request(i: int) -> None:
    await asyncio.sleep(0.1)   # 异步等待 0.1 秒，期间事件循环可处理其他协程


async def async_main() -> None:
    t0 = time.perf_counter()
    await asyncio.gather(*(async_request(i) for i in range(10)))
    print(f"异步版本总耗时：{time.perf_counter() - t0:.3f}s")


if __name__ == "__main__":
    sync_main()
    asyncio.run(async_main())
