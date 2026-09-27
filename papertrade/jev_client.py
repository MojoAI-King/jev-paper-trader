"""Minimal TypeSafe System One (Jev) client, stdlib only.

API contract (docs.typesafe.ai/api): POST https://api.typesafe.ai/v1/systemone
with {"model", "state", "questions"}; answers come back keyed by question id.
The official SDK is `typesafe-sdk` on PyPI; this client avoids the dependency.
"""
from __future__ import annotations

import json
import os
import random
import time
import urllib.error
import urllib.request
from pathlib import Path

API_URL = "https://api.typesafe.ai/v1/systemone"
RETRY_STATUSES = {429, 500, 502, 503, 529}
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class JevError(RuntimeError):
    """Any failure talking to Jev. Callers should fail safe, never guess."""

    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


def load_api_key() -> str:
    """Read the key from the environment or the project's .env file."""
    for name in ("TYPESAFE_AI_API_KEY", "TYPESAFE_API_KEY"):
        if os.environ.get(name):
            return os.environ[name].strip()
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            key, _, value = line.partition("=")
            if key.strip() in ("TYPESAFE_AI_API_KEY", "TYPESAFE_API_KEY") and value.strip():
                return value.strip().strip('"').strip("'")
    raise JevError("No API key found. Put TYPESAFE_AI_API_KEY=... in .env at the project root.")


def _http_post(url: str, body: dict, api_key: str, timeout: float) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:500]
        raise JevError(f"HTTP {e.code}: {detail}", status=e.code) from None
    except urllib.error.URLError as e:
        raise JevError(f"Network error: {e.reason}") from None
    except TimeoutError:
        raise JevError(f"Timed out after {timeout}s") from None


class JevClient:
    def __init__(self, model: str = "jev-latest", api_key: str | None = None,
                 timeout: float = 10.0, max_retries: int = 3, transport=None):
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self._transport = transport or _http_post
        # A custom transport (tests, dry runs) doesn't need a real key.
        self._api_key = api_key or ("" if transport else load_api_key())

    def ask(self, state, questions: dict) -> dict:
        """Send all questions over one state in a single request.

        Returns {"answers", "model", "usage", "latency_ms"}. Raises JevError.
        """
        body = {"model": self.model, "state": state, "questions": questions}
        attempt = 0
        while True:
            start = time.monotonic()
            try:
                data = self._transport(API_URL, body, self._api_key, self.timeout)
                break
            except JevError as e:
                if e.status not in RETRY_STATUSES or attempt >= self.max_retries:
                    raise
                time.sleep(min(8.0, 0.5 * 2 ** attempt) + random.random() * 0.25)
                attempt += 1
        answers = data.get("answers") or {}
        missing = set(questions) - set(answers)
        if missing:
            raise JevError(f"Response missing answers for: {sorted(missing)}")
        return {
            "answers": answers,
            "model": data.get("model"),
            "usage": data.get("usage"),
            "latency_ms": round((time.monotonic() - start) * 1000),
        }
