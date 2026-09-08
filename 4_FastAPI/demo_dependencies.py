"""依赖注入 Depends 的四种用法：函数依赖、类依赖、子依赖、yield 依赖。"""
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

app = FastAPI()


# 1) 函数依赖：把公共参数抽取出来复用
def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}


@app.get("/items/")
def read_items(commons: dict = Depends(common_parameters)):
    return commons


# 2) 类依赖：可以带状态
class Pagination:
    def __init__(self, page: int = 1, size: int = 10):
        self.page = page
        self.size = size


@app.get("/users/")
def list_users(p: Pagination = Depends(Pagination)):
    return {"page": p.page, "size": p.size}


# 3) 子依赖：依赖里还能依赖别的依赖
def get_current_user():
    return "alice"


def get_db(user: str = Depends(get_current_user)):
    return {"user": user, "conn": "数据库连接"}


@app.get("/me/")
def read_me(db: dict = Depends(get_db)):
    return db


# 4) yield 依赖：请求结束后清理（常用于关闭数据库会话）
def get_session():
    print("  [依赖] 打开数据库会话")
    try:
        yield "会话对象"
    finally:
        print("  [依赖] 关闭数据库会话")


@app.get("/with-session/")
def use_session(s: str = Depends(get_session)):
    return {"session": s}


if __name__ == "__main__":
    with TestClient(app) as client:
        print("函数依赖:", client.get("/items/?q=hi&skip=2&limit=5").json())
        print("类依赖:  ", client.get("/users/?page=3&size=20").json())
        print("子依赖:  ", client.get("/me/").json())
        print("yield依赖:", client.get("/with-session/").json())
