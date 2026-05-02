# Chapter 05 — Full voice loop

**Goals:** End-to-end voice with **blocking** vs **streaming** response, and **latency breakdown** with Rich.

- `blocking_voice_agent.py` — record → STT → LLM → TTS → play.
- `streaming_voice_agent.py` — optional text query arg; streams LLM tokens and speaks sentence chunks.
- `debug_latency.py` — colored table of stage timings.

**Next:** [06_real_time_systems/](../06_real_time_systems/).
