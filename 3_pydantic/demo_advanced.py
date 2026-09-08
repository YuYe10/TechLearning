"""Pydantic 进阶：computed_field / Annotated 复用 / alias / 泛型 / TypeAdapter。"""
from pydantic import BaseModel, Field, computed_field, TypeAdapter, ConfigDict
from typing import Annotated, Generic, TypeVar


# 1. computed_field：计算字段
class Rect(BaseModel):
    width: int
    height: int

    @computed_field
    @property
    def area(self) -> int:
        return self.width * self.height


# 2. Annotated + Field：复用约束
PositiveInt = Annotated[int, Field(gt=0)]


class Order(BaseModel):
    qty: PositiveInt
    price: PositiveInt


# 3. alias：别名（常用在 JSON 字段名与 Python 变量名不一致时）
class AliasModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    user_name: str = Field(alias="userName")


# 4. 泛型模型
T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int


class Book(BaseModel):
    title: str


def main():
    print("== 1. computed_field 计算字段 ==")
    r = Rect(width=3, height=4)
    print("  area:", r.area, "| dump:", r.model_dump())

    print("\n== 2. Annotated 复用约束 ==")
    print("  ", Order(qty=2, price=10))
    try:
        Order(qty=0, price=10)
    except Exception as e:
        print("  qty=0 ->", type(e).__name__)

    print("\n== 3. alias 别名 ==")
    a = AliasModel(userName="alice")
    print("  从别名构建:", a, "| 字段名访问:", a.user_name,
          "| dump(by_alias):", a.model_dump(by_alias=True))

    print("\n== 4. 泛型模型 ==")
    p = Page[Book](items=[Book(title="a"), Book(title="b")], total=2)
    print("  ", p.model_dump())

    print("\n== 5. TypeAdapter：单个类型也能校验 ==")
    ta = TypeAdapter(list[int])
    print("  校验:", ta.validate_python(["1", "2", "3"]))
    try:
        ta.validate_python([1, "x"])
    except Exception as e:
        print("  非法 ->", type(e).__name__)


if __name__ == "__main__":
    main()
