from __future__ import annotations

from app.models import StageResult, utc_now
from app.pipeline import STAGES
from app.store import store


def advance_company_run(company_run_id: str) -> dict:
    run = store.get(company_run_id)
    if run.status == "completed":
        return run.to_dict()
    if run.current_stage >= len(STAGES):
        run.status = "completed"
        store.save(run)
        return run.to_dict()

    run.status = "running"
    index = run.current_stage
    name, handler = STAGES[index]
    stage = StageResult(number=index + 1, name=name, status="running", started_at=utc_now())
    run.stages.append(stage)
    store.save(run)
    try:
        output = handler(run)
        stage.output = output
        stage.status = "completed"
        stage.completed_at = utc_now()
        run.context[f"stage_{index + 1}"] = output
        run.current_stage += 1
        if run.current_stage == len(STAGES):
            run.status = "completed"
    except Exception as exc:
        stage.status = "failed"
        stage.error = str(exc)
        stage.completed_at = utc_now()
        run.status = "failed"
    store.save(run)
    return run.to_dict()

