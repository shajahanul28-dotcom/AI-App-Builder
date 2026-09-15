from __future__ import annotations

import argparse
import json

from main import run


def main() -> None:
    parser = argparse.ArgumentParser(prog="novaix", description="NOVAIX AI App Builder")
    parser.add_argument("name", help="Name of the app to design")
    parser.add_argument("instruction", help="Tamil or English app instruction")
    args = parser.parse_args()
    print(json.dumps(run(args.name, args.instruction), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
