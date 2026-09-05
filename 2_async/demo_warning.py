"""演示：调用协程却不 await 会触发 RuntimeWarning

当我们调用一个 async 函数时，得到的是一个协程对象；如果从不 await 它，
Python 会发出警告：coroutine 'xxx' was never awaited。

运行本文件，观察 stderr 里的 RuntimeWarning。
"""

import asyncio


async def say_hi() -> str:
    print("这条不会被打印 —— 因为协程从未被 await")
    return "hi"


async def main() -> None:
    # 创建协程对象，但从不 await：协程被创建后立刻被丢弃，触发 RuntimeWarning
    say_hi()

    # 让事件循环多转几圈，确保警告有时间被打印出来
    await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())
