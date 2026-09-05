from typing import Any, Generator  # pyright: ignore[reportDeprecated]


def countdown(n) -> Generator[Any, Any, None]:
    while n > 0:
        yield n
        n -= 1
 
# 创建生成器对象
generator: Generator[int, Any, None] = countdown(n=5)
 
# 通过迭代生成器获取值
print(next(generator))  # 输出: 5
print(next(generator))  # 输出: 4
print(next(generator))  # 输出: 3
 
# 使用 for 循环迭代生成器
for value in generator:
    print(value)  # 输出: 2 1