"""WebSocket 双向通信（进阶）：回声服务器。"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.testclient import TestClient

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"回显: {data}")
    except WebSocketDisconnect:
        print("  客户端已断开")


if __name__ == "__main__":
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            ws.send_text("你好")
            print(ws.receive_text())
            ws.send_text("fastapi")
            print(ws.receive_text())
