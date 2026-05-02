# Chapter 10 — Deployment

**Goals:** **CLI** launcher (`voice-agent`), **WebSocket** server + minimal **browser client**, **Docker** skeleton.

```bash
# HTTP + WebSocket (from repo root)
uv run python 10_deployment/websocket_server.py
# Open http://127.0.0.1:8765/
```

Static assets live in `browser_client/`. Mount `models/` at runtime for LLM/STT/TTS in containers.

**Raspberry Pi:** Prefer CPU wheels for `llama-cpp-python`, smaller Whisper models, and shorter contexts; same pipeline as desktop.

**Next:** Iterate on your own product requirements.
