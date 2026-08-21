from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any

import torch
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer

from llm_eval.io_utils import read_jsonl, write_jsonl
from llm_eval.prompts import format_prompt, load_prompt_templates


def _cuda_usable() -> bool:
    if not torch.cuda.is_available():
        return False
    try:
        torch.zeros(1, device="cuda")
        return True
    except Exception:
        return False


def resolve_device(device: str) -> str:
    if device == "auto":
        return "cuda" if _cuda_usable() else "cpu"
    if device == "cuda" and not _cuda_usable():
        print("CUDA unavailable or broken; falling back to CPU.")
        return "cpu"
    return device


def load_causal_lm(hf_id: str, device: str, dtype: str):
    torch_dtype = getattr(torch, dtype, torch.float32)
    model = AutoModelForCausalLM.from_pretrained(hf_id, dtype=torch_dtype)
    tokenizer = AutoTokenizer.from_pretrained(hf_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.to(device)
    model.eval()
    return model, tokenizer


def generate_response(
    model,
    tokenizer,
    prompt: str,
    *,
    max_new_tokens: int,
    temperature: float,
    do_sample: bool,
    device: str,
) -> str:
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature if do_sample else None,
            do_sample=do_sample,
            pad_token_id=tokenizer.eos_token_id,
        )
    new_tokens = output_ids[0, inputs["input_ids"].shape[1] :]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


def response_id(model: str, prompt_id: str, question_id: str) -> str:
    raw = f"{model}|{prompt_id}|{question_id}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def run_behavioral_evaluation(
    *,
    study_id: str,
    questions_path: Path,
    templates_path: Path,
    output_dir: Path,
    models: list[dict[str, Any]],
    prompt_ids: list[str],
    device: str,
    dtype: str,
    temperature: float,
    do_sample: bool,
    limit: int | None = None,
    extra_response_fields: list[str] | None = None,
) -> list[Path]:
    questions = read_jsonl(questions_path)
    if limit:
        questions = questions[:limit]
    templates = load_prompt_templates(templates_path)
    device = resolve_device(device)
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    passthrough = extra_response_fields or []

    for model_cfg in models:
        name = model_cfg["name"]
        hf_id = model_cfg["hf_id"]
        max_new_tokens = model_cfg.get("max_new_tokens", 128)
        print(f"Loading {name} ({hf_id}) on {device}...")
        model, tokenizer = load_causal_lm(hf_id, device, dtype)

        for prompt_id in prompt_ids:
            if prompt_id not in templates:
                raise KeyError(f"Unknown prompt id: {prompt_id}")
            template = templates[prompt_id]["template"]
            rows: list[dict[str, Any]] = []
            for q in tqdm(questions, desc=f"{name}/{prompt_id}"):
                prompt = format_prompt(template, q)
                t0 = time.perf_counter()
                resp = generate_response(
                    model,
                    tokenizer,
                    prompt,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    do_sample=do_sample,
                    device=device,
                )
                latency_ms = (time.perf_counter() - t0) * 1000
                row: dict[str, Any] = {
                    "response_id": response_id(name, prompt_id, q["id"]),
                    "study": study_id,
                    "model": name,
                    "hf_id": hf_id,
                    "prompt_id": prompt_id,
                    "prompt_name": templates[prompt_id]["name"],
                    "question_id": q["id"],
                    "category": q.get("category"),
                    "prompt": prompt,
                    "response": resp,
                    "latency_ms": round(latency_ms, 2),
                }
                for key in passthrough:
                    if key in q:
                        row[key] = q[key]
                if "text" in q and "question_text" not in row:
                    row["question_text"] = q["text"]
                rows.append(row)

            out_path = output_dir / f"{name}_{prompt_id}.jsonl"
            write_jsonl(out_path, rows)
            written.append(out_path)
            print(f"Wrote {out_path} ({len(rows)} responses)")

        del model
        if device == "cuda":
            torch.cuda.empty_cache()

    return written
