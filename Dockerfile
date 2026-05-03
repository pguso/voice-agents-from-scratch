# Models are mounted at runtime (gitignored / large).
FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md LICENSE PLAN.md ./
COPY src ./src
COPY 00_start_here ./00_start_here
COPY 01_audio_io ./01_audio_io
COPY 02_speech_to_text ./02_speech_to_text
COPY 03_text_to_speech ./03_text_to_speech
COPY 04_agent_core ./04_agent_core
COPY 05_full_voice_loop ./05_full_voice_loop
COPY 06_real_time_systems ./06_real_time_systems
COPY 07_tools ./07_tools
COPY 08_personality ./08_personality
COPY 09_projects ./09_projects
COPY 10_deployment ./10_deployment
COPY diagrams ./diagrams

RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8765

CMD ["python", "10_deployment/legacy_local/websocket_server.py"]
