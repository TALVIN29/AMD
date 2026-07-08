"""Local model: a small quantized GGUF run on CPU via llama.cpp.

This is the token-cheap path. The grading box is 4 GB RAM / 2 vCPU / CPU-only, so
we bundle a 2-3B 4-bit model. Every task answered here costs ZERO tokens toward the
score, so the router sends the easy categories here.

Kept deliberately simple (no logprobs/logits_all) to stay within the 4 GB budget.
"""
import os

MODEL_PATH = os.environ.get("LOCAL_MODEL_PATH", "/models/local.gguf")
# CPU threads default to the 2 vCPU grading box; override for local dev.
N_THREADS = int(os.environ.get("LLAMA_THREADS", "2"))
N_CTX = int(os.environ.get("LLAMA_CTX", "4096"))

_llm = None


def _load():
    global _llm
    if _llm is None:
        from llama_cpp import Llama  # imported lazily so dry-run needs no model
        _llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=N_CTX,
            n_threads=N_THREADS,
            verbose=False,
        )
    return _llm


def answer(prompt: str, system: str, max_tokens: int = 256) -> str:
    llm = _load()
    out = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.0,
    )
    return out["choices"][0]["message"]["content"].strip()
