"""Task 与 gather：真正的「并发」

一个协程只能被顺序地 await；要同时运行多个协程，有两种常见做法：
1. asyncio.create_task()：把协程包装成 Task，交给事件循环并发调度；
2. asyncio.gather()：并发运行多个可等待对象，并一次性收集它们的返回值。
"""

import asyncio
import time


async def fetch(name: str, seconds: float) -> str:
    """模拟一次网络请求：耗时 seconds 秒后返回结果。"""
    print(f"  [{time.perf_counter():.3f}] {name} 开始")
    await asyncio.sleep(seconds)
    print(f"  [{time.perf_counter():.3f}] {name} 完成")
    return f"{name} 的结果"


async def main() -> None:
    # ---- 方式一：gather 一行并发运行 + 收集结果（最常用）----
    # 总耗时取决于最慢的那个（0.3s），而不是三者之和（0.6s）。
    t0 = time.perf_counter()
    results = await asyncio.gather(
        fetch("A", 0.3),
        fetch("B", 0.1),
        fetch("C", 0.2),
    )
    print(f"gather 总耗时：{time.perf_counter() - t0:.3f}s")
    print("结果：", results, "\n")

    # ---- 方式二：create_task 先包装成 Task，再逐个 await ----
    t1 = time.perf_counter()
    task_x = asyncio.create_task(fetch("X", 0.3))
    task_y = asyncio.create_task(fetch("Y", 0.1))

    # 从 create_task 那一刻起，两个 Task 已经在后台并发运行了
    result_x = await task_x
    result_y = await task_y
    print(f"create_task 总耗时：{time.perf_counter() - t1:.3f}s")
    print("结果：", [result_x, result_y])


if __name__ == "__main__":
    asyncio.run(main())
