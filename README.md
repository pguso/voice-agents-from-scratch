![banner.jpeg](diagrams/banner.jpeg)

# Voice agents from scratch

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![uv](https://img.shields.io/badge/uv-package%20manager-5A45FF?style=flat&logo=uv&logoColor=white)](https://docs.astral.sh/uv/)
[![GitHub stars](https://img.shields.io/github/stars/pguso/voice-agents-from-scratch?style=flat&logo=github&label=stars)](https://github.com/pguso/voice-agents-from-scratch)

Build **real-time voice agents** from the ground up - microphone → **STT** → **LLM** → **TTS** → speaker - with tools, personality, and streaming latency called out explicitly. This repo is a **hands-on tutorial**: numbered chapters, runnable scripts, and a small shared library under `src/voice_agents/`.

---

## What you need before you start

| Requirement | Notes |
|-------------|--------|
| **Python 3.11+** | Declared in `pyproject.toml` (`requires-python >= 3.11`). |
| **Microphone and speakers/headphones** | Examples record from the default input device and play to the default output. |
| **Disk space** | Roughly **~800 MB** for bundled tutorial models (Whisper tiny.en, Qwen 2.5 0.5B Q4 GGUF, Kokoro v1.0). `models/` is gitignored. |
| **Network** | Needed for `uv sync` (packages) and the first **`download_models.py`** run (Hugging Face + release URLs). |
| **PortAudio** | Used by `sounddevice`. On macOS it is often already satisfied; on Linux you may need your distro’s PortAudio dev package so `sounddevice` can load. |

Some lessons use extra dependency groups:

- **`vad`**  -  PyTorch + torchaudio for voice-activity and related examples (`uv sync --extra vad`).
- **`serve`**  -  FastAPI + Uvicorn + websockets for the local WebSocket server / browser client (`uv sync --extra serve`).
- **`deploy`**  -  Modal client for hosted deployment in chapter 10 (`uv sync --extra deploy`); combine with `serve` to run the ASGI app locally too.

---

## Install the toolchain

This project standardizes on **[uv](https://docs.astral.sh/uv/)** for environments and running scripts.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # once per machine
```

---

## Get the code and dependencies

```bash
git clone https://github.com/pguso/voice-agents-from-scratch.git
cd voice-agents-from-scratch

uv sync
```

Install optional groups only when you need them (you can combine extras, e.g. `uv sync --extra vad --extra serve --extra deploy`).

```bash
uv sync --extra vad
uv sync --extra serve
uv sync --extra deploy
```

---

## Verify audio and Python imports

```bash
uv run python 00_start_here/check_deps.py
```

You should see `OK` for each required module. A **WARN** on PortAudio usually means the OS cannot see an audio backend - fix that before relying on mic/speaker examples.

---

## Download models (first run)

```bash
uv run python 00_start_here/download_models.py
```

This populates **`models/`** (Whisper weights via `faster-whisper`, LLM GGUF via Hugging Face, Kokoro ONNX + voice bundle via HTTP). Safe to re-run; existing files are skipped.

---

## Run your first end-to-end voice agent

From the repository root:

```bash
uv run python 00_start_here/run_first_voice_agent.py
```

You will be prompted to record a few seconds of speech; the script transcribes with Whisper, replies with a local LLM, and speaks with Kokoro using a **streaming** pipeline so playback can start before the full reply is generated. Chapter zero explains the design in depth: **[00_start_here/README.md](00_start_here/README.md)**.

---

## Optional: interactive script launcher

```bash
uv run voice-agent
```

(or `uv run start`) opens a menu of common tutorial scripts. You can always run any script directly with `uv run python <path>`.

---

## If `llama-cpp-python` fails to install

Prebuilt wheels are often available from the [llama-cpp-python wheel index](https://abetlen.github.io/llama-cpp-python/). Platform-specific hints also live in **[00_start_here/README.md](00_start_here/README.md)**.

---

## How the course is organized

Each numbered folder is a chapter. Inside lesson folders you typically find a **`.py`** entry script and a **`CODE.md`** walkthrough. Shared building blocks live in **`src/voice_agents/`** (`audio`, `stt`, `tts`, `agent`, `tools`, …).

| Chapter | Topic |
|---------|--------|
| **[00_start_here](00_start_here/)** | First runnable agent, model download, architecture narrative |
| **[01_audio_io](01_audio_io/)** | Mic, speaker, WAV, streaming blocks, simple VAD-style debug |
| **[02_speech_to_text](02_speech_to_text/)** | Whisper: one-shot, streaming, partial results |
| **[03_text_to_speech](03_text_to_speech/)** | Kokoro: basics, streaming, profiles, latency |
| **[04_agent_core](04_agent_core/)** | Prompting, loops, memory, debugging |
| **[05_full_voice_loop](05_full_voice_loop/)** | Blocking vs streaming agents, latency tooling |
| **[06_real_time_systems](06_real_time_systems/)** | Turn-taking, interruption, duplex patterns |
| **[07_tools](07_tools/)** | Tool routing, calculator, time, weather, web search, LLM tool loops |
| **[08_personality](08_personality/)** | Style and emotional variation |
| **[09_projects](09_projects/)** | Larger compositions (CLI assistant, tutor, interviewer, …) |

Further reading:

- **[00_start_here/architecture_overview.md](00_start_here/architecture_overview.md)**  -  big-picture diagram and flow
- **[GLOSSARY.md](GLOSSARY.md)**  -  PCM, STT, TTS, VAD, …
- **[OPTIMIZE.md](OPTIMIZE.md)**  -  optional Apple Silicon notes (Metal / CoreML)

---

## License

See **[LICENSE](LICENSE)**.
