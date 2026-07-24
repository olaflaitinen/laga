# API

## `laga.repair(text, strict=False)`

Repairs malformed JSON and returns the parsed Python object.

Raises `LagaError` when the input cannot be repaired into valid JSON.

## `laga.repair_to_str(text, strict=False)`

Repairs malformed JSON and returns a normalized JSON string.

Raises `LagaError` when the input cannot be repaired into valid JSON.

## `laga.loads(text, strict=False)`

Alias for `laga.repair`.

## Duplicate Keys

If an object contains duplicate keys, the last value wins, matching Python dict behavior.

## `laga.LagaError`

Exception raised when repair fails. The message includes a character position when one is available.
