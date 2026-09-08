"""SQLAlchemy + SQLite 数据库 CRUD（进阶）。

运行方式：
    python demo_database.py
（用 SQLite 文件库，无需单独安装数据库服务）
"""
import os

from fastapi import FastAPI, Depends, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, Session, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)


Base.metadata.create_all(bind=engine)

app = FastAPI()


# yield 依赖：每个请求用独立的数据库会话，结束后关闭
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ItemCreate(BaseModel):
    name: str
    price: float


class ItemOut(ItemCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)  # 允许从 ORM 对象读取属性


@app.post("/items/", response_model=ItemOut)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = Item(name=item.name, price=item.price)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.get("/items/", response_model=list[ItemOut])
def list_items(db: Session = Depends(get_db)):
    return db.query(Item).all()


@app.get("/items/{item_id}", response_model=ItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.get(Item, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="未找到该商品")
    return db_item


if __name__ == "__main__":
    # 清空重建表，保证每次运行结果一致
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    try:
        with TestClient(app) as client:
            print("新增:", client.post("/items/", json={"name": "苹果", "price": 3.5}).json())
            print("新增:", client.post("/items/", json={"name": "香蕉", "price": 2.0}).json())
            print("列表:", client.get("/items/").json())
            print("单个:", client.get("/items/1").json())
            r = client.get("/items/999")
            print("查不存在 -> 状态码", r.status_code, "|", r.json())
    finally:
        engine.dispose()  # 释放连接池，之后才能删除 SQLite 文件
        if os.path.exists("test.db"):
            os.remove("test.db")
