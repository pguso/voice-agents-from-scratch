"""Minimal FastAPI + WebSocket JSON echo (optional local lab; chapter 10 uses Modal)."""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from voice_agents.agent.session_store import SessionStore

app = FastAPI(title="voice-agents-from-scratch")
sessions = SessionStore(ttl_s=3600)

HERE = Path(__file__).resolve().parent
STATIC = HERE / "browser_client"
if STATIC.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")


@app.get("/", response_model=None)
def index() -> FileResponse | PlainTextResponse:
    index_html = STATIC / "index.html"
    if index_html.is_file():
        return FileResponse(index_html)
    return PlainTextResponse("Add browser_client/index.html or open /docs")


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket) -> None:
    await ws.accept()
    sid = str(uuid.uuid4())
    sessions.update(sid, connected=True)
    await ws.send_json({"type": "hello", "session_id": sid})
    try:
        while True:
            msg = await ws.receive_json()
            if msg.get("type") == "text":
                sessions.update(sid, last_message=msg.get("content", ""))
            await ws.send_json({"type": "echo", "session_id": sid, "got": msg})
    except WebSocketDisconnect:
        sessions.delete(sid)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8765)
