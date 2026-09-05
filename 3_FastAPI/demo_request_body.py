"""Pydantic 请求体 + 字段校验 + response_model + 自动文档。"""
from typing import List

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, EmailStr, Field

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float = Field(gt=0, description="价格必须大于 0")
    tags: List[str] = []
    email: EmailStr | None = None


class ItemOut(BaseModel):
    name: str
    price: float


@app.post("/items/", response_model=ItemOut)
def create_item(item: Item):
    print("  收到请求体:", item.model_dump())
    return item  # 会被 response_model 过滤/校验，只返回 name 和 price


if __name__ == "__main__":
    with TestClient(app) as client:
        ok = client.post(
            "/items/",
            json={"name": "牙刷", "price": 9.9, "tags": ["日用"], "email": "a@b.com"},
        )
        print("正常请求 ->", ok.status_code, ok.json())

        bad = client.post("/items/", json={"name": "牙刷", "price": -1})
        print("price=-1  -> 状态码", bad.status_code, "| 错误:", bad.json()["detail"][0]["msg"])

        bad2 = client.post("/items/", json={"name": "牙刷", "price": 1, "email": "not-an-email"})
        print("email 非法 -> 状态码", bad2.status_code, "| 错误:", bad2.json()["detail"][0]["msg"])
