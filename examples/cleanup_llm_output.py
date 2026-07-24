from __future__ import annotations

import laga


def main() -> None:
    text = """Sure, here is the answer:
```json
{
  name: "Ada",
  skills: ["python", "json",],
  active: True,
}
```
"""
    print(laga.repair(text))
    print(laga.repair_to_str(text))


if __name__ == "__main__":
    main()
