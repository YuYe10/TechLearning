"""FastAPI 最小应用 + 路由 + 路径参数 + 查询参数。

运行方式：
    python demo_hello.py
（用 TestClient 直接调用接口，无需手动起服务）
"""
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI(title="Hello FastAPI", description="最小示例")


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}


@app.get("/users/{user_id}")
def read_user(user_id: int, name: str | None = None):
    # 路径参数 user_id 会被自动转成 int；查询参数 name 可选
    return {"user_id": user_id, "name": name}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = "默认值", flag: bool = False):
    return {"item_id": item_id, "q": q, "flag": flag}


if __name__ == "__main__":
    with TestClient(app) as client:
        print("GET /                    ->", client.get("/").json())
        print("GET /users/42            ->", client.get("/users/42").json())
        print("GET /users/42?name=alice ->", client.get("/users/42?name=alice").json())
        print("GET /items/7?q=hi&flag=t ->", client.get("/items/7?q=hi&flag=true").json())
        # 非法类型 → 422 校验错误
        r = client.get("/users/abc")
        print("GET /users/abc           -> 状态码", r.status_code, "| 错误:", r.json()["detail"][0]["msg"])
