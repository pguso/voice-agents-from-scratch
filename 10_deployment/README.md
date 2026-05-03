# Chapter 10 - Deployment (Modal.com)

**Goals:** Ship a **small HTTP API** on [Modal](https://modal.com) that runs **Llama-2-7B-Chat** as a **GGUF** via **llama-cpp-python** (CUDA on **T4**) and **Kokoro** TTS (**kokoro-onnx**), with weights cached on a **Modal Volume** so cold starts amortize after the first download.

This chapter is **cloud-first** (containers, GPU image, HTTPS endpoint). Chapters **0–9** stay **local-first** (Qwen GGUF under `models/llm/`, etc.). Here we use **TheBloke/Llama-2-7B-Chat-GGUF** (`llama-2-7b-chat.Q4_K_M.gguf`) and the **Llama-2 chat** prompt format—not the Qwen `<|im_start|>` template from [`AgentCore`](../src/voice_agents/agent/agent_core.py).

**Deeper dive:** [`modal_chapter/CODE.md`](modal_chapter/CODE.md) walks through the Modal pieces. Source: [`modal_app.py`](modal_app.py).

---

## Prerequisites

1. A [Modal](https://modal.com) account and workspace.
2. **Authenticate** the CLI (from repo root):

   ```bash
   uv sync --extra deploy
   uv run modal setup
   ```

   Or: `pip install modal` in your environment and `modal token new`.

3. **Optional:** Hugging Face token if your environment needs it for downloads:

   ```bash
   uv run modal secret create huggingface HF_TOKEN=hf_...
   ```

   The deploy script reads `HF_TOKEN` or `HUGGING_FACE_HUB_TOKEN` from the environment **inside the container**. To attach that secret to the app, add `secrets=[modal.Secret.from_name("huggingface")]` to the `@app.function` in [`modal_app.py`](modal_app.py) (not enabled by default so deploy works without secrets).

---

## Deploy

```bash
uv sync --extra deploy
uv run modal deploy 10_deployment/modal_app.py
```

Modal prints an **HTTPS** URL for the ASGI app. Endpoints:

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/health` | Liveness + which GGUF filename the app expects |
| `POST` | `/v1/reply` | JSON body → LLM reply + **base64 WAV** (PCM16) |

**Example** (replace the URL with yours from `modal deploy`):

```bash
curl -sS -X POST "https://YOUR-WORKSPACE--voice-agents-ch10-llama2-kokoro-web.modal.run/v1/reply" \
  -H "Content-Type: application/json" \
  -d '{"message":"Say hello in one short sentence."}' \
  | python -c "import sys,json,base64,pathlib; d=json.load(sys.stdin); pathlib.Path('reply.wav').write_bytes(base64.standard_b64decode(d['audio_wav_base64'])); print(d['text'])"
```

**Dev loop** (ephemeral URL, reload on file save):

```bash
uv run modal serve 10_deployment/modal_app.py
```

---

## What runs where

- **GPU `T4`:** **llama-cpp-python** is installed from the **CUDA 12.4** prebuilt wheel index (see `_LLAMA_CUDA_WHEEL_INDEX` in [`modal_app.py`](modal_app.py)). **Kokoro** uses **CPU** `onnxruntime` in the same container (lightweight vs. the 7B model).
- **Volume `voice-agents-llama2-kokoro-models`:** GGUF + Kokoro ONNX/voices persist across container cycles. First request may spend several minutes downloading the **~4 GB** GGUF; later requests reuse the volume.
- **Timeouts:** The Modal function uses a long `timeout` so first-time model download + load can finish.

---

## CPU-only or no GPU quota

The default app requests **`gpu="T4"`**. To experiment on **CPU only**:

1. In [`modal_app.py`](modal_app.py), change `gpu="T4"` to `gpu=None` (or omit `gpu`).
2. Change the image: install **`llama-cpp-python`** without the CUDA wheel index (plain `pip_install("llama-cpp-python")` only), and set `n_gpu_layers=0` in the `Llama(...)` constructor.

Expect much slower inference for **7B**.

---

## Legacy: local WebSocket echo

For a **local** FastAPI + WebSocket JSON echo (used by the repo **Dockerfile** smoke server), see [`legacy_local/websocket_server.py`](legacy_local/websocket_server.py):

```bash
uv run python 10_deployment/legacy_local/websocket_server.py
# Open http://127.0.0.1:8765/
```

---

## License note

**Llama 2** weights are subject to the [Meta Llama 2 license](https://ai.meta.com/resources/models-and-libraries/llama-downloads/). Use only in compliance with that license and your Modal / HF terms.
