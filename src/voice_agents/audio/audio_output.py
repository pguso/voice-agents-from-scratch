"""Speaker playback."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf


def play_wav_file(
    path: str | Path,
    *,
    on_playback_start: Callable[[], None] | None = None,
) -> None:
    data, sr = sf.read(str(path), always_2d=False)
    play_float_mono(
        np.asarray(data, dtype=np.float32),
        int(sr),
        on_playback_start=on_playback_start,
    )


def play_float_mono(
    samples: np.ndarray,
    sample_rate: int,
    *,
    on_playback_start: Callable[[], None] | None = None,
) -> None:
    """Play mono float audio (shape ``(n,)``)."""
    x = np.asarray(samples, dtype=np.float32)
    if x.ndim > 1:
        x = x[:, 0]
    if on_playback_start is not None:
        on_playback_start()
    sd.play(x, sample_rate)
    sd.wait()
