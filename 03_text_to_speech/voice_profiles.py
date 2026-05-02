"""Map simple profile names to Kokoro voice ids (edit to taste)."""

from __future__ import annotations

from dataclasses import dataclass

from voice_agents.tts.streaming_tts import TTSConfig, list_voices


@dataclass
class VoiceProfile:
    name: str
    kokoro_voice: str
    speed: float = 1.0


PROFILES: dict[str, VoiceProfile] = {
    "default": VoiceProfile("default", "af_heart"),
    "calm": VoiceProfile("calm", "af_bella", speed=0.95),
    "direct": VoiceProfile("direct", "am_adam", speed=1.05),
}


def resolve(config: TTSConfig, profile: str) -> TTSConfig:
    available = set(list_voices(config))
    p = PROFILES.get(profile, PROFILES["default"])
    voice = p.kokoro_voice if p.kokoro_voice in available else next(iter(available))
    return TTSConfig(
        model_path=config.model_path,
        voices_path=config.voices_path,
        voice=voice,
        speed=p.speed,
        lang=config.lang,
    )


if __name__ == "__main__":
    from pathlib import Path

    ROOT = Path(__file__).resolve().parents[1]
    cfg = TTSConfig(
        model_path=str(ROOT / "models/kokoro/kokoro-v1.0.onnx"),
        voices_path=str(ROOT / "models/kokoro/voices-v1.0.bin"),
    )
    for name in PROFILES:
        r = resolve(cfg, name)
        print(name, "→", r.voice, r.speed)
