"""Local (cheap) model inference. Runs on the AMD Developer Cloud GPU via ROCm.

Confidence is the average per-token probability of the generated answer -
a cheap proxy for "how sure is the model of this answer", no extra calls needed.
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from router.config import LOCAL_MODEL

_tokenizer = None
_model = None


def _load():
    global _tokenizer, _model
    if _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL)
        _model = AutoModelForCausalLM.from_pretrained(LOCAL_MODEL, torch_dtype=torch.bfloat16, device_map="auto")
    return _tokenizer, _model


def answer(prompt: str, max_new_tokens: int = 256) -> tuple[str, float]:
    """Returns (answer_text, confidence) where confidence is in [0, 1]."""
    tokenizer, model = _load()
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            output_scores=True,
            return_dict_in_generate=True,
        )

    generated_ids = out.sequences[0][inputs["input_ids"].shape[1]:]
    text = tokenizer.decode(generated_ids, skip_special_tokens=True)

    # Average probability the model assigned to the token it actually picked.
    token_probs = [
        torch.softmax(score[0], dim=-1)[token_id].item()
        for score, token_id in zip(out.scores, generated_ids)
    ]
    confidence = sum(token_probs) / len(token_probs) if token_probs else 0.0

    return text.strip(), confidence
