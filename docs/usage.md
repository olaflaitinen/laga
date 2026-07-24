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
```

You can also control output and safety limits:

```python
import laga

print(laga.repair_to_str('{"a": 1}', pretty=True))
print(laga.repair('{"a": 1}', duplicate_keys="error"))
```

The CLI accepts `--stdin`, `--pretty`, `--max-depth`, `--max-input-size`, and `--duplicate-keys` for more controlled workflows.

## Practical Guidance

- Use `repair` when you want a Python object.
- Use `repair_to_str` when you want canonical JSON text.
- Use `loads` if you want the familiar JSON-style name.
- Use `strict=True` for validation workflows where silent repair would hide a data issue.
