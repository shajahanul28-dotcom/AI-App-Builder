from recovered.main import run


if __name__ == "__main__":
    import json

    result = run(
        "AI App Builder",
        "Create a professional mobile app from Tamil or English instructions with secure storage, testing, preview and release metadata.",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))

