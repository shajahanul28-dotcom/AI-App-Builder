from __future__ import annotations

import json
from pathlib import Path
from threading import RLock

from .models import CompanyRun, utc_now


class RunStore:
    def __init__(self, path: str | Path = ".novaix/runs.json") -> None:
        self.path = Path(path)
        self.company_runs: dict[str, CompanyRun] = {}
        self._lock = RLock()
        self.load()

    def load(self) -> None:
        with self._lock:
            if not self.path.exists():
                return
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self.company_runs = {
                key: CompanyRun.from_dict(dict(value)) for key, value in data.items()
            }

    def save(self, run: CompanyRun) -> None:
        with self._lock:
            run.updated_at = utc_now()
            self.company_runs[run.id] = run
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_suffix(".tmp")
            temporary.write_text(
                json.dumps(
                    {key: value.to_dict() for key, value in self.company_runs.items()},
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            temporary.replace(self.path)

    def get(self, run_id: str) -> CompanyRun:
        try:
            return self.company_runs[run_id]
        except KeyError as exc:
            raise KeyError(f"Unknown company run: {run_id}") from exc


store = RunStore()

