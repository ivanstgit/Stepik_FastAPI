from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

# список для хранения подключённых WebSocket клиентов
connected_clients = []


# WebSocket-роут для обработки WebSocket подключений
@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        connected_clients.remove(websocket)


# роут для массовой рассылки сообщений всем подключённым клиентам
@app.get("/broadcast/")
async def broadcast_message(message: str):
    for client in connected_clients:
        await client.send_text(f"Broadcast message: {message}")
