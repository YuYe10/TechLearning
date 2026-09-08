"""Pydantic model_config 常用配置项。"""
from pydantic import BaseModel, ConfigDict, Field, ValidationError


# 1. extra：额外字段的处理
class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")
    a: int


# 2. validate_assignment：赋值时也校验
class Guarded(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    age: int = Field(gt=0)


# 3. 字符串归一化
class Normalize(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, str_to_lower=True)
    name: str


# 4. frozen：不可变
class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True)
    x: int


def main():
    print("== 1. extra=forbid：拒绝额外字段 ==")
    try:
        Strict(a=1, b=2)
    except ValidationError as e:
        print("  额外字段 b ->", e.errors()[0]["msg"])

    print("\n== 2. validate_assignment：赋值时校验 ==")
    g = Guarded(age=10)
    try:
        g.age = -1
    except ValidationError as e:
        print("  赋值 -1 ->", e.errors()[0]["msg"])

    print("\n== 3. 字符串归一化 ==")
    n = Normalize(name="  Alice  ")
    print("  name:", repr(n.name))

    print("\n== 4. frozen：不可变 ==")
    f = Frozen(x=1)
    try:
        f.x = 2
    except Exception as e:
        print("  修改被拒 ->", type(e).__name__)

    print("\n== 5. from_attributes：从任意属性对象读取（ORM 模式）==")
    class ORMUser(BaseModel):
        model_config = ConfigDict(from_attributes=True)
        id: int
        name: str

    class Row:  # 模拟数据库返回的对象
        def __init__(self, id, name):
            self.id, self.name = id, name

    u = ORMUser.model_validate(Row(1, "alice"))
    print("  ", u)


if __name__ == "__main__":
    main()
