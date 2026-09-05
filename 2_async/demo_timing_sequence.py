"""时序例子：多个协程在事件循环里如何「交错」执行

关键认知：asyncio 是单线程并发。当一个协程执行到 await 时，它会「让出」控制权，
事件循环立刻切换到另一个就绪的协程去运行。所以多个协程是「交错前进」的，
而不是排队等上一个完全结束。

下面用带时间戳的打印，观察两个协程是如何交替执行的。
"""

import asyncio
import time


async def worker(name: str, rounds: int) -> None:
    """一个 worker 协程：每轮 await sleep 让出控制权，共 rounds 轮。"""
    for i in range(rounds):
        print(f"  [{time.perf_counter():.3f}] {name} 第 {i} 轮开始")
        await asyncio.sleep(0.1)   # 在这里让出控制权，其他协程得以运行
        print(f"  [{time.perf_counter():.3f}] {name} 第 {i} 轮结束")


async def main() -> None:
    await asyncio.gather(
        worker("甲", 3),
        worker("乙", 3),
    )


if __name__ == "__main__":
    asyncio.run(main())
