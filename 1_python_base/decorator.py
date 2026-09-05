from typing import Callable


def my_decorator(func) -> Callable[..., None]:
    def wrapper(*args, **kwargs) -> None:
        print("执行前")
        func(*args, **kwargs)
        print("执行后")
    return wrapper

@my_decorator
def greet(name) -> None:
    print(f"Hello, {name}!")

greet("Alice")

def repeat(num_times) -> Callable[..., Callable[..., None]]:
    def decorator(func) -> Callable[..., None]:
        def wrapper(*args, **kwargs) -> None:
            for _ in range(num_times):
                func(*args, **kwargs)
        return wrapper
    return decorator

@repeat(num_times=5)
def say_hello() -> None:
    print("Hello!")

say_hello()