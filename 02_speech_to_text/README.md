# Chapter 02 — Speech to text

**Goals:** Full-file transcription, windowed “streaming” transcription, and **segment-level** partial results.

Requires Whisper weights under `models/whisper/` (run `00_start_here/download_models.py`).

- `transcribe_once.py` — one-shot file transcription.
- `streaming_transcription.py` — rolling windows from the mic.
- `handling_partial_results.py` — iterate Whisper segments with timestamps.

**Next:** [03_text_to_speech/](../03_text_to_speech/).
