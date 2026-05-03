"""LLM agent core using llama-cpp-python (chat-style prompts)."""

from __future__ import annotations

import ctypes
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Literal

from llama_cpp import Llama, llama_log_callback, llama_log_set

from voice_agents.agent.prompt_engine import PromptEngine

ChatTemplate = Literal["qwen25", "llama3"]


@llama_log_callback
def _silence_llama_cpp_logs(level: int, text: object, user_data: object) -> None:
    """Drop llama.cpp stderr spam (e.g. n_ctx vs n_ctx_train); exceptions still propagate in Python."""
    del level, text, user_data


llama_log_set(_silence_llama_cpp_logs, ctypes.c_void_p())


# Qwen2.5 instruct end-of-message token (string form for raw prompts)
_IM_END = "<|" + "im_end" + "|>"

@dataclass
class AgentMessage:
    role: str
    content: str


def qwen25_chat_prompt(system: str, user: str) -> str:
    """Open-format chat template for Qwen2.5 instruct GGUF models."""
    return (
        f"<|im_start|>system\n{system}{_IM_END}\n"
        f"<|im_start|>user\n{user}{_IM_END}\n"
        f"<|im_start|>assistant\n"
    )


def llama3_instruct_chat_prompt(system: str, user: str) -> str:
    """Chat template for Meta Llama 3 / 3.1 / 3.2 **instruct** GGUFs (llama.cpp raw prompt).

    Do **not** prefix with ``<|begin_of_text|>`` here: ``llama_cpp.Llama.__call__`` already
    prepends the model BOS when ``add_bos_token`` is enabled on the GGUF; duplicating that
    token triggers ``RuntimeWarning: Detected duplicate leading "<|begin_of_text|>"...``.
    """
    sh = "<|start_header_id|>"
    eh = "<|end_header_id|>"
    eot = "<|eot_id|>"
    return (
        f"{sh}system{eh}\n\n{system}{eot}"
        f"{sh}user{eh}\n\n{user}{eot}"
        f"{sh}assistant{eh}\n\n"
    )


@dataclass
class AgentCore:
    model_path: str
    n_ctx: int = 4096
    n_threads: int | None = None
    verbose: bool = False
    # Must match the GGUF family (e.g. chapter 09 capstones use ``llama3`` for Meta Llama 3.x instruct).
    chat_template: ChatTemplate = "qwen25"
    _llama: Llama | None = field(default=None, init=False, repr=False)

    def _llm(self) -> Llama:
        if self._llama is None:
            kwargs: dict = {
                "model_path": self.model_path,
                "n_ctx": self.n_ctx,
                "verbose": self.verbose,
            }
            if self.n_threads is not None:
                kwargs["n_threads"] = self.n_threads
            self._llama = Llama(**kwargs)
        return self._llama

    def preload(self) -> None:
        """Load the GGUF via llama.cpp so the first ``complete`` is not blocked on mmap/init."""
        self._llm()

    def complete(
        self,
        user_text: str,
        *,
        engine: PromptEngine | None = None,
        max_tokens: int = 256,
        temperature: float = 0.7,
        stop: list[str] | None = None,
    ) -> str:
        """Single-turn completion (blocking)."""
        eng = engine or PromptEngine()
        user_msg = eng.build_user_message(user_text)
        if self.chat_template == "llama3":
            prompt = llama3_instruct_chat_prompt(eng.system_prompt, user_msg)
            stop_tokens = stop or ["<|eot_id|>", "<|end_of_text|>"]
        else:
            prompt = qwen25_chat_prompt(eng.system_prompt, user_msg)
            stop_tokens = stop or [_IM_END, "<|endoftext|>"]
        llm = self._llm()
        out = llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=stop_tokens,
        )
        text = ""
        if out and "choices" in out:
            text = out["choices"][0]["text"].strip()
        eng.add_memory(f"User: {user_text}")
        eng.add_memory(f"Assistant: {text}")
        return text

    def stream_tokens(
        self,
        user_text: str,
        *,
        engine: PromptEngine | None = None,
        max_tokens: int = 256,
        temperature: float = 0.7,
        stop: list[str] | None = None,
    ) -> Iterator[str]:
        """Stream decoded token text chunks."""
        eng = engine or PromptEngine()
        user_msg = eng.build_user_message(user_text)
        if self.chat_template == "llama3":
            prompt = llama3_instruct_chat_prompt(eng.system_prompt, user_msg)
            stop_tokens = stop or ["<|eot_id|>", "<|end_of_text|>"]
        else:
            prompt = qwen25_chat_prompt(eng.system_prompt, user_msg)
            stop_tokens = stop or [_IM_END, "<|endoftext|>"]
        llm = self._llm()
        stream = llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=stop_tokens,
            stream=True,
        )
        buf: list[str] = []
        for chunk in stream:
            if chunk and "choices" in chunk:
                d = chunk["choices"][0].get("text", "")
                if d:
                    buf.append(d)
                    yield d
        full = "".join(buf).strip()
        eng.add_memory(f"User: {user_text}")
        eng.add_memory(f"Assistant: {full}")
