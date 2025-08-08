#app/main.py

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from prometheus_client import Counter, generate_latest
from starlette.responses import Response
from typing import Dict
import smtplib

import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL")

app = FastAPI()

connections = {}

def send_email_notification(username: str):
                subject = f"new chat user joined: {username}"
                body = f"a new user has joined the chat:{username}"
                msg = MIMEText(body)
                msg["Subject"] = subject
                msg["FROM"] = SMTP_USERNAME
                msg["To"] = NOTIFY_EMAIL

                try:
                    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                        server.starttls()
                        server.login(SMTP_USERNAME, SMTP_PASSWORD)
                        server.send_message(msg)
                    print(f" email sent:{username} joined")
                except Exception as e:
                    print(f"failed to send email: {e}")

active_connections: Dict[WebSocket, str] = {}


MESSAGE_COUNTER = Counter("chat_messages_total", "Total chat messages")

CONNECTIONS_COUNTER = Counter("chat_connections_total", "total websocket connections")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def get():
    return HTMLResponse(open("static/index.html").read())

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")

@app.websocket("/ws")
async def websocket_endpoint(websocket:WebSocket):

    username = websocket.query_params.get("user", "anonymous")
    print(f" connected username: {username}")

    await websocket.accept()


    CONNECTIONS_COUNTER.inc()
    active_connections[websocket] = username
    await broadcast(f" {username} joined the chat.")

    
    try:
        while True:
            message = await websocket.receive_text()
            MESSAGE_COUNTER.inc()
            await broadcast(f"{username}:{message}")
            
    except WebSocketDisconnect:
        del active_connections[websocket]
        await broadcast(f" {username} left the chat ")

async def broadcast(message: str):
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except:
            disconnected.append(connection)
    for conn in disconnected:
        active_connections.pop(conn, None)

