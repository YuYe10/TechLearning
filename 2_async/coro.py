from typing import Literal


import asyncio

async def nested() -> Literal[42]:
    return 42

async def main() -> None:
    # 如果我们只调用 "nested()" 则无事发生。
    # 一个协程对象被创建但是没有被等待，
    # 因此它 *根本不会运行*。
    nested()  # 将引发 "RuntimeWarning"。

    # 现在让我们等待它：
    print(await nested())  # 将打印 "42"。

asyncio.run(main())