"""表单 Form 与文件上传 UploadFile。"""
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.testclient import TestClient

app = FastAPI()


@app.post("/login/")
def login(username: str = Form(), password: str = Form()):
    return {"username": username}


@app.post("/upload/")
async def upload(file: UploadFile = File()):
    content = await file.read()
    return {"filename": file.filename, "size": len(content)}


if __name__ == "__main__":
    with TestClient(app) as client:
        r = client.post("/login/", data={"username": "alice", "password": "secret"})
        print("表单登录 ->", r.json())
        r2 = client.post("/upload/", files={"file": ("hello.txt", b"hello fastapi", "text/plain")})
        print("文件上传 ->", r2.json())
