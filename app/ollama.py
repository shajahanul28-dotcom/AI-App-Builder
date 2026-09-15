from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass
class OllamaClient:
    model: str = "qwen2.5-coder:1.5b"
    endpoint: str = "http://127.0.0.1:11434/api/generate"
    timeout: float = 120.0

    def generate(self, prompt: str) -> str:
        payload = json.dumps({"model": self.model, "prompt": prompt, "stream": False}).encode()
        request = urllib.request.Request(
            self.endpoint,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Ollama is unavailable: {exc}") from exc
        answer = body.get("response", "").strip()
        if not answer:
            raise RuntimeError("Ollama returned an empty response")
        return answer

    def health(self) -> bool:
        try:
            request = urllib.request.Request(self.endpoint.rsplit("/api/", 1)[0] + "/api/tags")
            with urllib.request.urlopen(request, timeout=2) as response:
                return response.status == 200
        except (urllib.error.URLError, TimeoutError):
            return False

