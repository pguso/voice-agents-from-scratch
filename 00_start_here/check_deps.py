"""Optional dependency and runtime checks (exit 0 = OK)."""

from __future__ import annotations

import importlib
import sys


def _try_import(name: str) -> bool:
    try:
        importlib.import_module(name)
        return True
    except Exception:
        return False


def main() -> int:
    ok = True
    required = [
        "sounddevice",
        "soundfile",
        "numpy",
        "faster_whisper",
        "llama_cpp",
        "pydantic",
        "rich",
        "httpx",
        "kokoro_onnx",
        "huggingface_hub",
    ]
    for mod in required:
        if _try_import(mod):
            print(f"OK  {mod}")
        else:
            print(f"MISSING  {mod}")
            ok = False

    try:
        import sounddevice as sd

        _ = sd.query_devices()
        print("OK  PortAudio (sounddevice query_devices)")
    except Exception as e:
        print(f"WARN  sounddevice/PortAudio: {e}")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
