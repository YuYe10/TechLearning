"""Pydantic 序列化与反序列化：model_dump / model_dump_json / model_validate / model_validate_json / json_schema。"""
from pydantic import BaseModel, Field


class Item(BaseModel):
    name: str
    price: float = Field(gt=0)
    secret: str = Field(exclude=True)   # 序列化时默认排除该字段


def main():
    item = Item(name="牙刷", price=9.9, secret="不要外传")

    print("== 1. model_dump 转字典 ==")
    d = item.model_dump()
    print("  ", d, "| secret 被排除:", "secret" not in d)

    print("\n== 2. model_dump_json 转 JSON 字符串 ==")
    s = item.model_dump_json()
    print("  ", s, "| 类型:", type(s).__name__)

    print("\n== 3. model_validate 从字典构建 ==")
    i2 = Item.model_validate({"name": "铅笔", "price": 2.5, "secret": "x"})
    print("  ", i2)

    print("\n== 4. model_validate_json 从 JSON 字符串构建 ==")
    i3 = Item.model_validate_json('{"name": "橡皮", "price": 1.5, "secret": "y"}')
    print("  ", i3)

    print("\n== 5. model_json_schema 导出 JSON Schema ==")
    schema = Item.model_json_schema()
    print("  字段:", list(schema.get("properties", {}).keys()))
    print("  price 约束:", schema["properties"]["price"])


if __name__ == "__main__":
    main()
