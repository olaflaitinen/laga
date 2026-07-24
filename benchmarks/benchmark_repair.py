from __future__ import annotations

import platform
import sys
import timeit

import laga

SAMPLES: list[tuple[str, str, bool]] = [
    ("strict-fast-path", '{"name": "Ada", "active": true, "roles": ["admin"]}', True),
    ("dirty-config", "{name: 'Ada', active: True, roles: ['admin',],}", False),
    (
        "llm-output",
        "Here is the result:\n```json\n{'name': 'Ada', 'active': True}\n```",
        False,
    ),
]


def main() -> None:
    print(f"python={sys.version.split()[0]} platform={platform.platform()}")
    for label, sample, strict in SAMPLES:
        duration = timeit.timeit(
            lambda sample=sample, strict=strict: laga.repair(sample, strict=strict),
            number=500,
        )
        print(f"{label}: {duration:.6f}s {sample[:40]}")


if __name__ == "__main__":
    main()
