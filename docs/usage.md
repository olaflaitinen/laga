# Usage

```python
import laga

text = "{name: 'Ada', active: True, roles: ['admin',]}"
data = laga.repair(text)
print(data)
```

The `strict` flag disables ambiguous recoveries. Use it when you want to fail fast on malformed structure instead of guessing.

```python
import laga

print(laga.repair('{"a": 1,}', strict=False))
print(laga.repair_to_str('{"a": 1,}'))
print(laga.repair_file('sample.json'))
```

You can also control output and safety limits:

```python
import laga

print(laga.repair_to_str('{"a": 1}', pretty=True))
print(laga.repair('{"a": 1}', duplicate_keys="error"))
```

The CLI accepts `--stdin`, `--pretty`, `--max-depth`, `--max-input-size`, and `--duplicate-keys` for more controlled workflows.
Use `--input` and `--output` when you want to repair files directly from the command line.

## Decision Guide

- Use `json.loads` when the input is already valid JSON.
- Use `repair` when the input is noisy or model-generated.
- Use `repair_file` when you are working with files on disk.
- Use `strict=True` when you want repairs to stop at ambiguous structure.
- Use `duplicate_keys="error"` when duplicate object members should fail.

## Practical Guidance

- Use `repair` when you want a Python object.
- Use `repair_to_str` when you want canonical JSON text.
- Use `loads` if you want the familiar JSON-style name.
- Use `strict=True` for validation workflows where silent repair would hide a data issue.
