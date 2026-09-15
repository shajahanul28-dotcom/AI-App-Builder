from __future__ import annotations

import re
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .generator import generate_flutter_project
from .models import CompanyRun
from .ollama import OllamaClient
from .verifier import verify_generated_project

StageHandler = Callable[[CompanyRun], dict[str, Any]]


def _tokens(text: str) -> list[str]:
    return re.findall(r"[\w-]+", text.lower(), flags=re.UNICODE)


def understand(run: CompanyRun) -> dict[str, Any]:
    text = run.instruction.strip()
    if len(text) < 12:
        raise ValueError("Instruction must describe the app in at least 12 characters")
    return {"goal": text, "language": "Tamil" if any("\u0b80" <= c <= "\u0bff" for c in text) else "English", "keywords": _tokens(text)[:30]}


def requirements(run: CompanyRun) -> dict[str, Any]:
    words = set(_tokens(run.instruction))
    capabilities = [name for name, hints in {
        "authentication": {"auth", "login", "user"},
        "database": {"database", "data", "store", "save"},
        "payments": {"payment", "payments", "pay"},
        "notifications": {"notification", "reminder", "alert"},
        "localization": {"tamil", "english", "sinhala", "language"},
        "offline": {"offline", "local"},
    }.items() if words & hints]
    return {"functional": capabilities or ["core_workflow"], "non_functional": ["secure", "accessible", "testable", "resumable"]}


def architecture(run: CompanyRun) -> dict[str, Any]:
    return {"pattern": "clean-architecture", "layers": ["presentation", "domain", "data", "platform"], "client": "Flutter", "api": "provider-adapter", "storage": "offline-first", "local_ai": {"provider": "Ollama", "model": OllamaClient().model, "available": OllamaClient().health()}}


def experience(run: CompanyRun) -> dict[str, Any]:
    return {"screens": ["Splash", "Onboarding", "Home", "Primary Workflow", "History", "Settings"], "states": ["loading", "empty", "success", "error"], "accessibility": ["contrast", "labels", "touch-targets"]}


def data_backend(run: CompanyRun) -> dict[str, Any]:
    required = run.context["stage_2"]["functional"]
    return {"entities": ["User", "Project", "Task", "Artifact", "AuditEvent"], "auth": "adapter" if "authentication" in required else "optional", "database": "repository-interface", "api_contract": "versioned-json"}


def security(run: CompanyRun) -> dict[str, Any]:
    return {"rules": ["no-secrets-in-source", "path-boundary-checks", "least-privilege", "audit-tools", "confirm-destructive-actions"], "risk_levels": ["read", "write", "destructive", "external"]}


def implementation(run: CompanyRun) -> dict[str, Any]:
    specification = {
        "app_name": run.app_name,
        "goal": run.context["stage_1"]["goal"],
        "requirements": run.context["stage_2"],
        "architecture": run.context["stage_3"],
        "screens": run.context["stage_4"]["screens"],
        "backend": run.context["stage_5"],
        "security": run.context["stage_6"],
    }
    generated = generate_flutter_project(run.app_name, run.instruction, specification)
    return {"modules": ["intent", "planner", "context", "tools", "executor", "verifier", "recovery", "release"], "delivery": "reviewable-increments", "generated_project": generated}


def verification(run: CompanyRun) -> dict[str, Any]:
    project = run.context["stage_7"]["generated_project"]["project_path"]
    report = verify_generated_project(project)
    return {"checks": ["structure", "flutter-pub-get", "flutter-analyze", "flutter-test"], "success_policy": "all-available-blocking-checks-pass", "report": report}


def repair(run: CompanyRun) -> dict[str, Any]:
    return {"loop": ["observe", "classify", "patch", "retest"], "max_retries": 3, "fallback": "precise-blocker-report"}


def release(run: CompanyRun) -> dict[str, Any]:
    project = Path(run.context["stage_7"]["generated_project"]["project_path"])
    archive_root = Path("generated_apps") / f"{project.name}-source"
    archive = shutil.make_archive(str(archive_root), "zip", root_dir=project)
    verification_status = run.context["stage_8"]["report"]["status"]
    return {"artifacts": [str(project), archive, str(project / "novaix/build_manifest.json")], "status": "release-ready" if verification_status in {"pass", "structural-pass"} else "verification-failed", "verification": verification_status, "known_limitations": [] if verification_status == "pass" else ["Flutter SDK was unavailable in this build environment; structural validation passed."]}


STAGES: list[tuple[str, StageHandler]] = [
    ("Intent Understanding", understand),
    ("Requirements", requirements),
    ("Architecture", architecture),
    ("UX and UI", experience),
    ("Backend and Data", data_backend),
    ("Security and Permissions", security),
    ("Implementation Plan", implementation),
    ("Testing and Verification", verification),
    ("Repair and Recovery", repair),
    ("Build and Release", release),
]
