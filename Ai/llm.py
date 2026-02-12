"""
Call local Ollama API (localhost:11434), return parsed JSON {dimension, metric, chart_type}.
"""
import json
import re

import requests

from Ai.prompt import build_prompt

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:7b"
TIMEOUT = 12


def call_ollama(prompt: str) -> str:
    r = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": prompt, "stream": False},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r.json().get("response", "")


def parse_json_from_response(text: str) -> dict:
    text = text.strip()
    match = re.search(r"\{[^{}]*\"dimension\"[^{}]*\"metric\"[^{}]*\"chart_type\"[^{}]*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
    return {}


def get_analysis_plan(user_message: str, source_cfg: dict) -> dict:
    """Build prompt from source config, call Ollama, return parsed plan."""
    columns_description = ", ".join(source_cfg["columns"])
    prompt = build_prompt(
        user_message,
        dimensions=source_cfg["dimensions"],
        metrics=source_cfg["metrics"],
        dimension_labels=source_cfg["dimension_labels"],
        metric_labels=source_cfg["metric_labels"],
        columns_description=columns_description,
    )
    response = call_ollama(prompt)
    return parse_json_from_response(response)
