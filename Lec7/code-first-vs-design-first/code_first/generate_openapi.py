"""Generate a versioned OpenAPI document from the Code-First application."""

import argparse
from pathlib import Path

from app import api


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default="v1", help="Folder version, for example v1 or v2")
    args = parser.parse_args()

    output = Path(__file__).parent / "openapi" / args.version / "openapi.yaml"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(api.spec.to_yaml(), encoding="utf-8")
    print(f"Generated {output}")


if __name__ == "__main__":
    main()
