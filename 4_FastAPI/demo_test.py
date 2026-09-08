"""用 pytest + TestClient 编写接口测试（进阶）。

运行方式：
    pytest demo_test.py -v
"""
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


@app.get("/add/{a}/{b}")
def add(a: int, b: int):
    return {"result": a + b}


client = TestClient(app)


def test_add():
    assert client.get("/add/1/2").json() == {"result": 3}


def test_add_type_error():
    assert client.get("/add/a/b").status_code == 422
