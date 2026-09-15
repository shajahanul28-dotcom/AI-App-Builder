from app.final.service import bootstrap_from_instruction
from app.company.service import advance_company_run
from app.store import store

def run(app_name: str, instruction: str):
    result = bootstrap_from_instruction(app_name, instruction)

    company_run_id = result["company_run_id"]
    while store.company_runs[company_run_id].status not in {"completed", "failed"}:
        advance_company_run(company_run_id)

    company_run = store.company_runs[company_run_id]

    final = {
        **result,
        "company_status": company_run.status,
        "current_stage": company_run.current_stage,
        "stages": [stage.__dict__ for stage in company_run.stages],
        "message": "Stages 1-10 completed." if company_run.status == "completed" else "Run stopped with a reported failure.",
    }
    return final

if __name__ == "__main__":
    example_instruction = (
        "Create a professional mobile app from Tamil or English instructions. "
        "Plan architecture, design UI, prepare backend/auth/database/payments, "
        "use a secure coding workspace, test, propose repairs, build, preview, "
        "and prepare store release metadata."
    )
    import json
    print(json.dumps(run("AI App Builder", example_instruction), indent=2, ensure_ascii=False))
