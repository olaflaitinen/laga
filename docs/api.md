# API

## `laga.repair(text, strict=False)`

Repairs malformed JSON and returns the parsed Python object.

Raises `LagaError` when the input cannot be repaired into valid JSON.

## `laga.repair_to_str(text, strict=False)`

Repairs malformed JSON and returns a normalized JSON string.

Raises `LagaError` when the input cannot be repaired into valid JSON.

When called with `pretty=True`, the output uses two-space indentation.

## `laga.repair_file(path, strict=False)`

Reads a file from disk, repairs its contents, and returns the parsed Python object.

Raises `LagaError` when the file contents cannot be repaired into valid JSON.

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

If you want duplicate object members to fail instead of being merged, pass `duplicate_keys="error"`.

## CLI Options

The CLI understands these options:

- `--stdin`: read input from standard input
- `--input PATH`: read input from a file
- `--output PATH`: write repaired JSON to a file
- `--pretty`: format output with two-space indentation
- `--compact`: force compact output
- `--quiet`: suppress standard output on success
- `--max-depth`: set the maximum nesting depth
- `--max-input-size`: reject oversized input before parsing
- `--duplicate-keys`: choose `last` or `error`

## `laga.LagaError`

Exception raised when repair fails. The message includes line and column information when available, plus a compact context snippet for easier debugging.
