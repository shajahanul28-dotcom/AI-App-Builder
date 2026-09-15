from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

RunStatus = Literal["pending", "running", "failed", "completed"]
StageStatus = Literal["pending", "running", "failed", "completed"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class StageResult:
    number: int
    name: str
    status: StageStatus = "pending"
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    started_at: str | None = None
    completed_at: str | None = None


@dataclass
class CompanyRun:
    app_name: str
    instruction: str
    id: str = field(default_factory=lambda: uuid4().hex)
    status: RunStatus = "pending"
    current_stage: int = 0
    stages: list[StageResult] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "CompanyRun":
        stages = [StageResult(**item) for item in value.pop("stages", [])]
        return cls(stages=stages, **value)

