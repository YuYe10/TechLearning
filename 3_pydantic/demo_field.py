"""Pydantic Field 约束与常用字段类型。"""
from pydantic import BaseModel, Field, EmailStr, ValidationError
from enum import Enum
from typing import Literal
from datetime import date
from uuid import UUID


class Role(str, Enum):
    admin = "admin"
    user = "user"


class Product(BaseModel):
    name: str = Field(min_length=2, max_length=20, description="商品名")
    price: float = Field(gt=0, le=10000)          # 大于 0 且小于等于 10000
    quantity: int = Field(ge=0)                    # 大于等于 0
    sku: str = Field(pattern=r"^[A-Z]{2}-\d{4}$")  # 正则匹配
    email: EmailStr                                # 邮箱格式
    role: Role = Role.user                         # 枚举
    level: Literal["low", "mid", "high"] = "low"   # 字面量
    released: date                                 # 日期
    uid: UUID                                      # UUID
    tags: list[str] = Field(default_factory=list)  # 可变默认值推荐用 default_factory


def main():
    print("== 1. 合法实例 ==")
    p = Product(name="钢笔", price=9.9, quantity=5, sku="AB-1234",
                email="a@b.com", role="admin", level="high",
                released="2024-01-15", uid="12345678-1234-5678-1234-567812345678")
    print("  ", p)
    print("  uid 类型:", type(p.uid).__name__, "| released 类型:", type(p.released).__name__)

    print("\n== 2. 各约束被破坏时的报错 ==")
    cases = [
        dict(name="x", price=9.9, quantity=1, sku="AB-1234", email="a@b.com",
             released="2024-01-15", uid="12345678-1234-5678-1234-567812345678"),  # name 太短
        dict(name="钢笔", price=-1, quantity=1, sku="AB-1234", email="a@b.com",
             released="2024-01-15", uid="12345678-1234-5678-1234-567812345678"),  # price <= 0
        dict(name="钢笔", price=9.9, quantity=1, sku="ab-1234", email="a@b.com",
             released="2024-01-15", uid="12345678-1234-5678-1234-567812345678"),  # sku 不匹配
        dict(name="钢笔", price=9.9, quantity=1, sku="AB-1234", email="not-an-email",
             released="2024-01-15", uid="12345678-1234-5678-1234-567812345678"),  # 邮箱非法
    ]
    for c in cases:
        try:
            Product(**c)
            print("  通过")
        except ValidationError as e:
            err = e.errors()[0]
            print("  拒绝:", err["loc"], "->", err["msg"])


if __name__ == "__main__":
    main()
