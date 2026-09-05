from typing import Any, Callable


x: Callable[..., Any] = lambda a, b: a * b
print(x(5, 6))