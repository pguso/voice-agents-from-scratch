"""Modal.com deployment: Llama-2-7B-Chat (GGUF) + Kokoro TTS over FastAPI ASGI.

Deploy: ``modal deploy 10_deployment/modal_app.py``
Dev:     ``modal serve 10_deployment/modal_app.py``

Requires a Modal account and ``modal`` CLI authenticated (``modal token new``).
"""

from __future__ import annotations

import base64
import io
import os
from pathlib import Path

import modal

APP_NAME = "voice-agents-ch10-llama2-kokoro"
MODELS_MOUNT = "/models"
VOLUME_NAME = "voice-agents-llama2-kokoro-models"

LLM_REPO = "TheBloke/Llama-2-7B-Chat-GGUF"
LLM_FILE = "llama-2-7b-chat.Q4_K_M.gguf"
KOKORO_ONNX_URL = (
    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
)
KOKORO_VOICES_URL = (
    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"
)

# Prebuilt CUDA wheels (host driver on Modal is recent; cu124 matches many T4/A10 pools).
_LLAMA_CUDA_WHEEL_INDEX = "https://abetlen.github.io/llama-cpp-python/whl/cu124"

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "fastapi[standard]>=0.115.0",
        "huggingface-hub>=0.24.0",
        "httpx>=0.27.0",
        "kokoro-onnx>=0.2.0",
        "onnxruntime>=1.17.0",
        "numpy>=1.26.0",
        "soundfile>=0.12.1",
        "uvicorn[standard]>=0.32.0",
    )
    .pip_install(
        "llama-cpp-python>=0.3.0",
        extra_index_url=_LLAMA_CUDA_WHEEL_INDEX,
    )
)

model_volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)
app = modal.App(APP_NAME)


def llama2_chat_prompt(*, system: str, user: str) -> str:
    """Llama-2-chat single-turn template (not Qwen ``<|im_start|>`` format)."""
    return (
        "<s>[INST] <<SYS>>\n"
        f"{system}\n"
        "<</SYS>>\n\n"
        f"{user.strip()} [/INST]"
    )


def _default_system_prompt() -> str:
    return (
        "You are a helpful, concise assistant. "
        "Reply in plain text suitable for speech synthesis; favor short sentences."
    )


@app.function(
    image=image,
    gpu="T4",
    volumes={MODELS_MOUNT: model_volume},
    timeout=60 * 60,
    scaledown_window=10 * 60,
)
@modal.concurrent(max_inputs=8)
@modal.asgi_app()
def web():
    import numpy as np
    import soundfile as sf
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import JSONResponse
    from huggingface_hub import hf_hub_download
    from kokoro_onnx import Kokoro
    from llama_cpp import Llama
    from pydantic import BaseModel, Field

    root = Path(MODELS_MOUNT)
    llm_dir = root / "llm"
    kokoro_dir = root / "kokoro"
    llm_path = llm_dir / LLM_FILE
    kokoro_onnx = kokoro_dir / "kokoro-v1.0.onnx"
    kokoro_voices = kokoro_dir / "voices-v1.0.bin"

    def _download_http(url: str, dest: Path) -> None:
        import httpx

        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and dest.stat().st_size > 0:
            return
        with httpx.Client(follow_redirects=True, timeout=600.0) as client:
            with client.stream("GET", url) as r:
                r.raise_for_status()
                with open(dest, "wb") as f:
                    for chunk in r.iter_bytes(1024 * 256):
                        f.write(chunk)
        model_volume.commit()

    def ensure_models() -> None:
        llm_dir.mkdir(parents=True, exist_ok=True)
        kokoro_dir.mkdir(parents=True, exist_ok=True)
        if not llm_path.is_file() or llm_path.stat().st_size < 1_000_000:
            token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
            hf_hub_download(
                repo_id=LLM_REPO,
                filename=LLM_FILE,
                local_dir=str(llm_dir),
                token=token,
            )
            model_volume.commit()
        if not kokoro_onnx.is_file():
            _download_http(KOKORO_ONNX_URL, kokoro_onnx)
        if not kokoro_voices.is_file():
            _download_http(KOKORO_VOICES_URL, kokoro_voices)

    ensure_models()

    # Resolve GGUF path (hf_hub_download may add repo subdirs depending on version).
    if not llm_path.is_file():
        found = list(llm_dir.rglob(LLM_FILE))
        if not found:
            raise RuntimeError(f"GGUF missing under {llm_dir} after download")
        gguf_path = str(found[0])
    else:
        gguf_path = str(llm_path)

    _llama: Llama | None = None
    _kokoro: Kokoro | None = None

    def get_llama() -> Llama:
        nonlocal _llama
        if _llama is None:
            _llama = Llama(
                model_path=gguf_path,
                n_ctx=4096,
                n_gpu_layers=-1,
                verbose=False,
            )
        return _llama

    def get_kokoro() -> Kokoro:
        nonlocal _kokoro
        if _kokoro is None:
            _kokoro = Kokoro(str(kokoro_onnx), str(kokoro_voices))
        return _kokoro

    class ReplyBody(BaseModel):
        message: str = Field(..., min_length=1, max_length=4000)
        system: str | None = Field(default=None, max_length=8000)
        voice: str | None = Field(default=None, description="Kokoro voice id, e.g. af_heart")
        max_tokens: int = Field(default=256, ge=8, le=1024)

    web_app = FastAPI(title="voice-agents-ch10", version="0.1.0")

    @web_app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "llm_gguf": LLM_FILE}

    @web_app.post("/v1/reply")
    def reply(body: ReplyBody) -> JSONResponse:
        system = body.system.strip() if body.system else _default_system_prompt()
        prompt = llama2_chat_prompt(system=system, user=body.message)
        llm = get_llama()
        out = llm(
            prompt,
            max_tokens=body.max_tokens,
            temperature=0.7,
            stop=["</s>", "[INST]"],
        )
        text = ""
        if out and out.get("choices"):
            text = str(out["choices"][0]["text"]).strip()
        if not text:
            raise HTTPException(status_code=500, detail="Empty LLM output")

        k = get_kokoro()
        voices = k.get_voices()
        voice = body.voice if body.voice and body.voice in voices else next(iter(voices))
        samples, sr = k.create(text, voice=voice, speed=1.0, lang="en-us")
        pcm = np.asarray(samples, dtype=np.float32).reshape(-1)
        if pcm.size == 0:
            raise HTTPException(status_code=500, detail="TTS produced no audio")
        clip = np.clip(pcm, -1.0, 1.0)
        int16 = (clip * 32767.0).astype(np.int16)
        buf = io.BytesIO()
        sf.write(buf, int16, int(sr), format="WAV", subtype="PCM_16")
        wav_b64 = base64.standard_b64encode(buf.getvalue()).decode("ascii")
        return JSONResponse(
            {
                "text": text,
                "voice": voice,
                "sample_rate": int(sr),
                "audio_wav_base64": wav_b64,
            }
        )

    return web_app
