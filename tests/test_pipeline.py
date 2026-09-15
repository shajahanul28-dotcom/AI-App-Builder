import tempfile
import json
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from app.final.service import bootstrap_from_instruction
from app.generator import generate_flutter_project
from app.models import CompanyRun
from app.server import NovaixHandler
from app.store import RunStore
from app.verifier import _flutter_command, verify_generated_project
from app.workspace import SafeWorkspace
from main import run


class PipelineTests(unittest.TestCase):
    def test_complete_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            isolated = RunStore(Path(directory) / "runs.json")
            with (
                patch("app.company.service.store", isolated),
                patch("app.final.service.store", isolated),
                patch("recovered.main.store", isolated),
            ):
                result = run(
                    "DueMate",
                    "Create a reminder app with notifications, offline data and Tamil language support",
                )
            self.assertEqual(result["company_status"], "completed")
            self.assertEqual(result["current_stage"], 10)
            self.assertEqual(len(result["stages"]), 10)
            self.assertTrue(all(stage["status"] == "completed" for stage in result["stages"]))
            self.assertTrue(isolated.path.exists())

    def test_rejects_empty_name(self) -> None:
        with self.assertRaisesRegex(ValueError, "App name"):
            bootstrap_from_instruction(" ", "Create a complete mobile app")

    def test_company_run_round_trip(self) -> None:
        original = CompanyRun(app_name="Test", instruction="Build a useful test application")
        restored = CompanyRun.from_dict(original.to_dict())
        self.assertEqual(restored.id, original.id)
        self.assertEqual(restored.app_name, "Test")

    def test_generator_creates_flutter_project(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = generate_flutter_project(
                "My App",
                "Create a useful offline mobile application",
                {"screens": ["Home", "History", "Settings"]},
                directory,
            )
            report = verify_generated_project(result["project_path"], run_flutter=False)
            self.assertEqual(result["package"], "my_app")
            self.assertEqual(report["status"], "structural-pass")
            self.assertTrue((Path(result["project_path"]) / "lib/main.dart").exists())
            manifest = json.loads((Path(result["project_path"]) / "novaix/build_manifest.json").read_text())
            self.assertEqual(manifest["version"], "1.2.0")

    def test_windows_flutter_batch_uses_cmd(self) -> None:
        with patch("app.verifier.os.name", "nt"):
            command = _flutter_command(r"C:\\flutter\\bin\\flutter.bat", ["pub", "get"])
        self.assertEqual(command[:4], ["cmd.exe", "/d", "/s", "/c"])
        self.assertIn("flutter.bat", command[4])

    def test_flutter_os_error_is_reported_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = generate_flutter_project(
                "Windows App",
                "Create a useful offline mobile application",
                {"screens": ["Home"]},
                directory,
            )
            with (
                patch("app.verifier.shutil.which", return_value=r"C:\\flutter\\bin\\flutter.bat"),
                patch("app.verifier.subprocess.run", side_effect=FileNotFoundError("missing runner")),
            ):
                report = verify_generated_project(result["project_path"])
        self.assertEqual(report["status"], "failed")
        self.assertIn("missing runner", report["commands"][0]["output"])

    def test_workspace_blocks_path_escape(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = SafeWorkspace(directory)
            with self.assertRaisesRegex(ValueError, "escapes"):
                workspace.write_text("../outside.txt", "blocked")

    def test_dashboard_health_and_build_api(self) -> None:
        server = ThreadingHTTPServer(("127.0.0.1", 0), NovaixHandler)
        server.access_token = "test-token"
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base = f"http://127.0.0.1:{server.server_port}"
            with urllib.request.urlopen(base + "/health") as response:
                self.assertEqual(json.load(response)["status"], "ok")
            payload = json.dumps({"name": "QuickTask", "instruction": "Create an offline task app with history and notifications"}).encode()
            request = urllib.request.Request(base + "/api/build", data=payload, headers={"Content-Type": "application/json", "X-NOVAIX-Token": "test-token"}, method="POST")
            with urllib.request.urlopen(request) as response:
                result = json.load(response)
            self.assertEqual(result["company_status"], "completed")
            self.assertTrue(result["download_url"].endswith(".zip"))
            unauthorized = urllib.request.Request(base + "/api/build", data=payload, headers={"Content-Type": "application/json"}, method="POST")
            with self.assertRaises(urllib.error.HTTPError) as denied:
                urllib.request.urlopen(unauthorized)
            self.assertEqual(denied.exception.code, 401)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
