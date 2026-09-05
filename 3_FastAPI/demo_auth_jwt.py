"""JWT 认证流程（进阶）：登录发 token，受保护接口校验 token。"""
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.testclient import TestClient

SECRET = "super-secret-key-for-demo-please-keep-it-long"
ALGORITHM = "HS256"

app = FastAPI()


def create_token(username: str, expires_min: int = 30) -> str:
    payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expires_min),
    }
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)


def get_current_user(authorization: str = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少 token")
    token = authorization[7:]
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="token 已过期")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="token 无效")
    return payload["sub"]


@app.post("/login/")
def login(username: str):
    return {"access_token": create_token(username), "token_type": "bearer"}


@app.get("/me/")
def me(username: str = Depends(get_current_user)):
    return {"username": username}


if __name__ == "__main__":
    with TestClient(app) as client:
        token = client.post("/login/?username=alice").json()["access_token"]
        print("登录拿到 token:", token[:30] + "...")
        r0 = client.get("/me/")
        print("不带 token -> 状态码", r0.status_code, "|", r0.json())
        r1 = client.get("/me/", headers={"Authorization": f"Bearer {token}"})
        print("带 token   ->", r1.status_code, r1.json())
        expired = create_token("alice", expires_min=-1)  # 已经过期的 token
        r2 = client.get("/me/", headers={"Authorization": f"Bearer {expired}"})
        print("过期 token -> 状态码", r2.status_code, "|", r2.json())
