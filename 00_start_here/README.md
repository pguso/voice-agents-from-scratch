# Chapter 00 — Start here

**Goal:** Run a full **mic → STT → LLM → TTS → speaker** pipeline on your machine with local models only.

## Stack (see root [PLAN.md](../PLAN.md))

| Piece | Library |
|-------|---------|
| Audio | `sounddevice`, `soundfile`, `numpy` |
| STT | `faster-whisper` |
| LLM | `llama-cpp-python` + Qwen2.5 GGUF |
| TTS | **Kokoro** (`kokoro-onnx`) — pure Python, no extra binary |

### Piper vs Kokoro for chapter 00

[PLAN.md](../PLAN.md) mentions **Piper** in the “easiest setup” table and **Kokoro** in the tech stack. **This chapter uses Kokoro** so `download_models.py` + `run_first_voice_agent.py` work after `uv sync` **without** installing a separate Piper CLI binary. **Chapter 03** demonstrates additional voices (including Piper-style workflows where relevant).

## Setup

```bash
uv sync
uv run python 00_start_here/download_models.py
uv run python 00_start_here/check_deps.py
uv run python 00_start_here/run_first_voice_agent.py
```

Or: `uv run voice-agent` (interactive menu).

## `llama-cpp-python` install issues

If `uv sync` tries to **compile** `llama-cpp-python` and fails (no C++ toolchain), use prebuilt wheels from the project index:

```bash
UV_EXTRA_INDEX_URL=https://abetlen.github.io/llama-cpp-python/whl/metal \
  uv sync
```

On **CPU-only** macOS / Linux, try the `cpu` index:

```bash
UV_EXTRA_INDEX_URL=https://abetlen.github.io/llama-cpp-python/whl/cpu \
  uv sync
```

See [llama-cpp-python wheels](https://github.com/abetlen/llama-cpp-python#supported-backends) for Metal / CUDA / CPU variants.

## Files

| File | Purpose |
|------|---------|
| `download_models.py` | Whisper, Qwen GGUF, Kokoro ONNX + voices → `models/` |
| `run_first_voice_agent.py` | 5s recording → reply → play |
| `check_deps.py` | Import + PortAudio sanity check (exit 0/1) |
| `architecture_overview.md` | Data flow and sequence (Mermaid) |

## Approximate download size

~500MB total on first `download_models.py` (Whisper tiny + small LLM + Kokoro). Re-runs skip existing files.
