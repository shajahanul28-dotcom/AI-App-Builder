from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


def _flutter_command(executable: str, arguments: list[str]) -> list[str]:
    """Build a cross-platform command, including Windows .bat launchers."""
    if os.name == "nt":
        command_line = subprocess.list2cmdline([executable, *arguments])
        return ["cmd.exe", "/d", "/s", "/c", command_line]
    return [executable, *arguments]


def verify_generated_project(project_path: str | Path, run_flutter: bool = True) -> dict[str, Any]:
    root = Path(project_path)
    required = ["pubspec.yaml", "lib/main.dart", "test/widget_test.dart", "novaix/specification.json", "novaix/build_manifest.json"]
    missing = [name for name in required if not (root / name).is_file()]
    flutter = shutil.which("flutter")
    report: dict[str, Any] = {"required_files": "pass" if not missing else "fail", "missing": missing, "flutter_available": bool(flutter), "commands": []}
    if missing or not run_flutter or not report["flutter_available"]:
        report["status"] = "failed" if missing else "structural-pass"
        return report
    for arguments in (["pub", "get"], ["analyze"], ["test"]):
        display_command = "flutter " + " ".join(arguments)
        command = _flutter_command(str(flutter), arguments)
        try:
            completed = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=300)
        except subprocess.TimeoutExpired as exc:
            report["commands"].append({"command": display_command, "exit_code": -1, "output": f"Timed out after {exc.timeout} seconds"})
            report["status"] = "failed"
            return report
        except OSError as exc:
            report["commands"].append({"command": display_command, "exit_code": -1, "output": str(exc)})
            report["status"] = "failed"
            return report
        report["commands"].append({"command": display_command, "exit_code": completed.returncode, "output": (completed.stdout + completed.stderr)[-4000:]})
        if completed.returncode:
            report["status"] = "failed"
            return report
    report["status"] = "pass"
    return report
