# `modal_app.py` — code walkthrough

Source file: [`../modal_app.py`](../modal_app.py) (repo root: `10_deployment/modal_app.py`).

## Purpose

This is the **capstone deployment** example: the same *idea* as earlier chapters (user text → **LLM** → **TTS audio**), but the runtime is **Modal** (managed containers, autoscaling HTTPS) instead of your laptop.

| Local stack (chapters 00–09) | This chapter |
|------------------------------|--------------|
| Qwen2.5 GGUF + `qwen25_chat_prompt` in [`AgentCore`](../../src/voice_agents/agent/agent_core.py) | **Llama-2-7B-Chat** GGUF + **Llama-2** `[INST]` / `<<SYS>>` string prompt in `modal_app.py` |
| Models in `models/` on disk | Models on a **Modal Volume** under `/models` |
| `llama-cpp-python` on your OS (Metal / CUDA / CPU) | **CUDA wheel** (`cu124` index) on **Linux T4** in the image |
| Kokoro files from [`download_models.py`](../../00_start_here/download_models.py) | Same Kokoro URLs, downloaded **inside** the container into the volume |

---

## Modal building blocks

1. **`modal.Image`** — Declares the container: Debian slim, Python 3.12, pip packages. **Two** `pip_install` chains: general deps, then **`llama-cpp-python`** from the **abetlen** CUDA wheel index so you do not compile llama.cpp on Modal yourself.

2. **`modal.Volume.from_name(..., create_if_missing=True)`** — Named durable disk. Mounted at `MODELS_MOUNT` (`/models`) so the **GGUF** and **Kokoro** files survive after the container scales down.

3. **`@app.function`** — Configures **GPU**, **volumes**, **timeout**, and the **image** for this worker pool.

4. **`@modal.concurrent(max_inputs=...)`** — Allows multiple in-flight HTTP requests per container (ASGI async).

5. **`@modal.asgi_app()`** — The decorated function **returns a FastAPI app**; Modal exposes it at a `*.modal.run` URL.

6. **`volume.commit()`** — After writing new files to the mount (downloads), **commit** pushes changes to durable volume storage (see [Modal volumes guide](https://modal.com/docs/guide/volumes)).

---

## Lifecycle inside `web()`

1. **`ensure_models()`** — If the GGUF is missing, **`hf_hub_download`** pulls **TheBloke/Llama-2-7B-Chat-GGUF** / `llama-2-7b-chat.Q4_K_M.gguf` into `/models/llm/`. Kokoro ONNX + `voices-v1.0.bin` are fetched over **HTTPS** (same URLs as chapter 00). Optional **`HF_TOKEN`** is passed through for gated hubs.

2. **Resolve GGUF path** — `hf_hub_download` layout can vary; **`rglob(LLM_FILE)`** picks the actual path.

3. **Lazy singletons** — `get_llama()` / `get_kokoro()` construct **`Llama`** and **`Kokoro`** once per container.

4. **`POST /v1/reply`** — Builds **`llama2_chat_prompt`**, runs **`llama(...)`** with stops **`</s>`** and **`[INST]`**, synthesizes with **`kokoro.create`**, writes **16-bit PCM WAV** to a buffer via **soundfile**, returns JSON with **`audio_wav_base64`**.

---

## Run / deploy

From the **repository root**:

```bash
uv sync --extra deploy
uv run modal deploy 10_deployment/modal_app.py
```

---

## See also

- [Chapter README](../README.md) — curl example, secrets, CPU fallback notes.
- [Modal web endpoints](https://modal.com/docs/guide/webhooks) — ASGI and cold starts.
