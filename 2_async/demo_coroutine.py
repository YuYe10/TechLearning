"""协程基础：async def / await / asyncio.run

核心要点：
1. 用 `async def` 定义的函数是「协程函数」，调用它只会创建一个协程对象，并不会执行。
2. 必须用 `await` 等待一个协程，它才会真正运行。
3. 顶层入口统一用 `asyncio.run(...)` 来启动整个程序。
"""

import asyncio


async def add(a: int, b: int) -> int:
    """一个最简协程：异步地「计算」a + b。"""
    print(f"  -> add({a}, {b}) 开始执行")
    await asyncio.sleep(0)          # 让出控制权（详见 demo_timing_sequence.py）
    print(f"  -> add({a}, {b}) 执行完毕")
    return a + b


async def main() -> None:
    # 1) 只调用、不 await：得到一个协程对象，什么也不会发生
    coro = add(1, 2)
    print("只调用不 await，得到的只是一个协程对象：")
    print("  ", coro)

    # 2) await 之后，协程才真正运行
    print("\nawait 之后：")
    result = await coro
    print(f"  结果 = {result}")


if __name__ == "__main__":
    asyncio.run(main())
