# Voice agents from scratch

Build **real-time voice agents** from the ground up—no black boxes. This repo is a **step-by-step learning journey**: microphone → STT → LLM → TTS → speaker, plus tools, personality, and deployment.

See **[PLAN.md](PLAN.md)** for the full roadmap, tech stack, and chapter outline.

## Quick start

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # install uv (once)
cd voice-agents-from-scratch
uv sync
uv run python 00_start_here/download_models.py      # first run: downloads ~500MB into models/
uv run python 00_start_here/run_first_voice_agent.py
```

If `llama-cpp-python` fails to install from source, use the [extra wheel index](https://abetlen.github.io/llama-cpp-python/) (documented in [00_start_here/README.md](00_start_here/README.md)).

## Layout

| Path | Purpose |
|------|---------|
| `00_start_here/` … `10_deployment/` | Tutorial chapters and runnable examples |
| `src/voice_agents/` | Reusable library (`audio`, `stt`, `tts`, `agent`, `tools`) |
| `models/` | Downloaded weights (gitignored) |
| `PLAN.md` | Compass and feature roadmap |

## Learn more

- Chapter zero: [00_start_here/README.md](00_start_here/README.md)
- Architecture: [00_start_here/architecture_overview.md](00_start_here/architecture_overview.md)

## License

See [LICENSE](LICENSE).
