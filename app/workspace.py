from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "novaix_app"


class SafeWorkspace:
    """Writes generated files only below one explicit project root."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def resolve(self, relative_path: str) -> Path:
        candidate = (self.root / relative_path).resolve()
        if candidate != self.root and self.root not in candidate.parents:
            raise ValueError(f"Path escapes project workspace: {relative_path}")
        return candidate

    def write_text(self, relative_path: str, content: str) -> Path:
        target = self.resolve(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(target.suffix + ".tmp")
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(target)
        return target

    def write_json(self, relative_path: str, value: Any) -> Path:
        return self.write_text(relative_path, json.dumps(value, indent=2, ensure_ascii=False) + "\n")

