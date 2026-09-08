"""Pydantic 基础：BaseModel 定义、类型转换、默认值、可选字段、ValidationError。"""
from pydantic import BaseModel, ValidationError


class User(BaseModel):
    id: int
    name: str
    score: float
    is_active: bool = True          # 有默认值 -> 可选字段
    tags: list[str] = []            # 可变默认值在 Pydantic 里是安全的（每次实例会复制）
    nickname: str | None = None     # 可选，可为 None


def main():
    print("== 1. 正常实例化 ==")
    u = User(id=1, name="alice", score=98.5)
    print("  ", u)
    print("  字段访问:", u.id, u.name, u.score)

    print("\n== 2. 类型自动转换 ==")
    u2 = User(id="2", name="bob", score="80")   # str -> int / float 自动转换
    print("  ", u2, "| score 类型:", type(u2.score).__name__)

    print("\n== 3. 默认值与可选字段 ==")
    u3 = User(id=3, name="carol", score=70)
    print("  is_active:", u3.is_active, "| tags:", u3.tags, "| nickname:", u3.nickname)

    print("\n== 4. 非法输入 -> ValidationError ==")
    try:
        User(id="abc", name="dave", score=0)
    except ValidationError as e:
        print("  错误数量:", e.error_count())
        for err in e.errors():
            print("   ", err["loc"], "->", err["msg"])


if __name__ == "__main__":
    main()
