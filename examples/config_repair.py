from __future__ import annotations

import laga


def main() -> None:
    text = "{path: 'C:/temp', retries: 3, timeout: 5,}"
    config = laga.loads(text)
    print(config)


if __name__ == "__main__":
    main()
