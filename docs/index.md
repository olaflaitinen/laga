# laga

`laga` repairs malformed JSON and returns Python objects.

It is designed for language model output, configuration text, and other inputs that are close to JSON but not quite valid.

## What It Does

- Parses valid JSON through the standard library first.
- Repairs the common failure modes from model output and ad hoc config.
- Returns plain Python data structures, not a custom AST.
- Keeps runtime dependencies at zero.

## Supported Repairs

- Trailing commas.
- Missing commas.
- Single quotes around strings and keys.
- Unquoted identifier keys.
- Python literals such as `True`, `False`, and `None`.
- Line comments and block comments.
- Markdown code fences.
- Curly quotes.
- Leading or trailing prose around the JSON payload.
- Truncated arrays and objects.
