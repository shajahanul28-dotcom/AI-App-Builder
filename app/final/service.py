from __future__ import annotations

from app.models import CompanyRun
from app.store import store


def bootstrap_from_instruction(app_name: str, instruction: str) -> dict:
    if not app_name.strip():
        raise ValueError("App name is required")
    run = CompanyRun(app_name=app_name.strip(), instruction=instruction.strip())
    store.save(run)
    return {"company_run_id": run.id, "app_name": run.app_name, "status": run.status}

