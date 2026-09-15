# NOVAIX AI App Builder

NOVAIX converts a Tamil or English app instruction into a persistent, resumable ten-stage delivery run and generates a runnable Flutter starter project. The recovered Library entrypoint is preserved in `recovered/main.py` and completed by the missing runtime modules.

## Pipeline

1. Intent understanding
2. Requirements
3. Architecture
4. UX and UI
5. Backend and data
6. Security and permissions
7. Implementation plan
8. Testing and verification
9. Repair and recovery
10. Build and release

Generated projects are written below `generated_apps/<app_name>/`. Each output contains Flutter source, a widget test, the complete NOVAIX specification, a build manifest, and a source ZIP. When Flutter is installed, NOVAIX runs `pub get`, `analyze`, and `test`; otherwise it records a structural verification result.

Local AI support uses Ollama at `http://127.0.0.1:11434` and defaults to `qwen2.5-coder:1.5b`, matching the lightweight NOVAIX laptop setup.

## Run

```bash
python main.py
python -m app.cli "My App" "Create a secure offline-first Flutter app"
```

## Visual dashboard

Laptop only:

```bash
python -m app.server
```

Laptop and phone on the same Wi-Fi:

```bash
python -m app.server --host 0.0.0.0
```

Open the secure URL printed by NOVAIX. The dashboard accepts Tamil or English instructions and returns a downloadable Flutter project ZIP.

On Windows, run `INSTALL_WINDOWS.ps1` once. Afterwards double-click `START_NOVAIX.bat`. For iPhone access on the same Wi-Fi, double-click `START_NOVAIX_PHONE.bat` and open the printed address on the phone.

The phone and laptop must be connected to the same Wi-Fi network. Keep the black NOVAIX window open while using the phone dashboard. Windows Firewall may ask once for permission; allow access on private networks.

## Stage 99 — Full testing

```bash
python -m compileall -q app recovered main.py tests
python -m unittest discover -s tests -v
```

## Stage 100 — Final build

```bash
python -m pip wheel . --no-deps --no-build-isolation -w dist
```

Run state is written atomically to `.novaix/runs.json`, allowing interrupted runs to be inspected and resumed safely.
