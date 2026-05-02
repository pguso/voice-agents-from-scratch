# Chapter 01 — Audio I/O

**Goals:** Capture microphone audio, play audio back, and see simple **VAD** (voice vs silence) using energy thresholds.

- `mic_input.py` — short fixed recording, print levels.
- `speaker_output.py` — play a test tone or a WAV path.
- `record_to_file.py` — record to `tmp/recorded.wav`.
- `stream_basics.py` — live RMS meter.
- `vad_debug.py` — per-block speech/silence labels (tune `THRESH`).

**Next:** [02_speech_to_text/](../02_speech_to_text/).
