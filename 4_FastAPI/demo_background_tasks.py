"""后台任务 BackgroundTasks：响应立即返回，慢操作放到后台。"""
import time

from fastapi import FastAPI, BackgroundTasks
from fastapi.testclient import TestClient

app = FastAPI()


def send_email(email: str, message: str):
    # 模拟耗时操作（发邮件、写日志等）
    time.sleep(0.2)
    print(f"  [后台任务] 已向 {email} 发送：{message}")


@app.post("/users/")
def create_user(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, email, "欢迎注册！")
    return {"status": "用户已创建", "email": email}


if __name__ == "__main__":
    with TestClient(app) as client:
        r = client.post("/users/?email=a@b.com")
        print(r.json())
        print("（真实服务里，客户端在后台任务完成前就已拿到响应；TestClient 会等后台任务跑完）")
