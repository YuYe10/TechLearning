"""中间件 + CORS + HTTPException + 自定义异常处理器。"""
import time

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

app = FastAPI()


# 自定义中间件：给每个响应加一个「处理耗时」头
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    cost = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time"] = f"{cost:.2f}ms"
    return response


# CORS 中间件：允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "hello"}


@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id == 0:
        raise HTTPException(status_code=404, detail="item not found")
    return {"item_id": item_id}


# 自定义异常处理器：捕获 ValueError 返回结构化错误
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"error": str(exc)})


@app.get("/boom")
def boom():
    raise ValueError("这是自定义的 ValueError")


if __name__ == "__main__":
    with TestClient(app) as client:
        r = client.get("/")
        print("GET /        ->", r.status_code, r.json(), "| 耗时头:", r.headers.get("x-process-time"))
        r2 = client.get("/items/0")
        print("GET /items/0 ->", r2.status_code, r2.json())
        r3 = client.get("/boom")
        print("GET /boom    ->", r3.status_code, r3.json())
        r4 = client.get("/", headers={"Origin": "http://example.com"})
        print("带 Origin 头 -> CORS 响应头:", r4.headers.get("access-control-allow-origin"))
