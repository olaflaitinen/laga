# API

## `laga.repair(text, strict=False)`

Repairs malformed JSON and returns the parsed Python object.

Raises `LagaError` when the input cannot be repaired into valid JSON.

## `laga.repair_to_str(text, strict=False)`

Repairs malformed JSON and returns a normalized JSON string.

Raises `LagaError` when the input cannot be repaired into valid JSON.

## `laga.loads(text, strict=False)`

Alias for `laga.repair`.

## Repair Options

The repair functions also accept these optional keyword arguments:

- `max_depth`: limits how deeply nested repaired JSON may be.
- `max_input_size`: rejects inputs that exceed a character limit before parsing.
- `duplicate_keys`: set to `"last"` for Python dict behavior or `"error"` to reject duplicate object keys.
- `pretty`: when using `repair_to_str`, pretty-print the output with two-space indentation.

## Duplicate Keys

If an object contains duplicate keys, the last value wins, matching Python dict behavior.

## `laga.LagaError`

Exception raised when repair fails. The message includes a character position when one is available.
