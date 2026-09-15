from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any


def verify_generated_project(project_path: str | Path, run_flutter: bool = True) -> dict[str, Any]:
    root = Path(project_path)
    required = ["pubspec.yaml", "lib/main.dart", "test/widget_test.dart", "novaix/specification.json", "novaix/build_manifest.json"]
    missing = [name for name in required if not (root / name).is_file()]
    report: dict[str, Any] = {"required_files": "pass" if not missing else "fail", "missing": missing, "flutter_available": bool(shutil.which("flutter")), "commands": []}
    if missing or not run_flutter or not report["flutter_available"]:
        report["status"] = "failed" if missing else "structural-pass"
        return report
    for command in (["flutter", "pub", "get"], ["flutter", "analyze"], ["flutter", "test"]):
        completed = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=300)
        report["commands"].append({"command": " ".join(command), "exit_code": completed.returncode, "output": (completed.stdout + completed.stderr)[-4000:]})
        if completed.returncode:
            report["status"] = "failed"
            return report
    report["status"] = "pass"
    return report

