from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any, Literal

from .errors import LagaError
from .tokenizer import _Token, _Tokenizer

__all__ = ["loads", "main", "repair", "repair_to_str"]

_MAX_NESTING_DEPTH = 256
_MAX_INPUT_SIZE: int | None = None
DuplicateKeyPolicy = Literal["last", "error"]

_SMART_QUOTES = str.maketrans(
    {
        chr(0x201C): '"',
        chr(0x201D): '"',
        chr(0x201E): '"',
        chr(0x201F): '"',
        chr(0x2018): "'",
        chr(0x2019): "'",
        chr(0x201A): "'",
    }
)
_LITERAL_MAP = {"true": True, "false": False, "null": None, "none": None}


def repair(
    text: str,
    *,
    strict: bool = False,
    max_depth: int = _MAX_NESTING_DEPTH,
    max_input_size: int | None = _MAX_INPUT_SIZE,
    duplicate_keys: DuplicateKeyPolicy = "last",
) -> Any:
    """Parse text as JSON, repairing common errors when needed.

    Args:
        text: Input text that should contain JSON.
        strict: When `True`, reject ambiguous repairs such as missing commas or
            truncated containers.

    Returns:
        The parsed Python value.

    Raises:
        LagaError: If the text cannot be repaired into valid JSON.
    """

    _validate_limits(
        max_depth=max_depth,
        max_input_size=max_input_size,
        duplicate_keys=duplicate_keys,
    )
    _check_input_size(text, max_input_size=max_input_size)
    if duplicate_keys == "last":
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return _repair_text(
                text,
                strict=strict,
                max_depth=max_depth,
                max_input_size=max_input_size,
                duplicate_keys=duplicate_keys,
            )
    return _repair_text(
        text,
        strict=strict,
        max_depth=max_depth,
        max_input_size=max_input_size,
        duplicate_keys=duplicate_keys,
    )


def repair_to_str(
    text: str,
    *,
    strict: bool = False,
    max_depth: int = _MAX_NESTING_DEPTH,
    max_input_size: int | None = _MAX_INPUT_SIZE,
    duplicate_keys: DuplicateKeyPolicy = "last",
    pretty: bool = False,
) -> str:
    """Repair JSON text and return normalized JSON.

    Args:
        text: Input text that should contain JSON.
        strict: When `True`, reject ambiguous repairs such as missing commas or
            truncated containers.

    Returns:
        A normalized JSON string.

    Raises:
        LagaError: If the text cannot be repaired into valid JSON.
    """

    if pretty:
        return json.dumps(
            repair(
                text,
                strict=strict,
                max_depth=max_depth,
                max_input_size=max_input_size,
                duplicate_keys=duplicate_keys,
            ),
            ensure_ascii=False,
            indent=2,
        )
    return json.dumps(
        repair(
            text,
            strict=strict,
            max_depth=max_depth,
            max_input_size=max_input_size,
            duplicate_keys=duplicate_keys,
        ),
        ensure_ascii=False,
        separators=(",", ":"),
    )


loads = repair


def main(argv: Iterable[str] | None = None) -> int:
    """Run a small command line interface for manual repair checks.

    Args:
        argv: Optional argument sequence. When omitted, `sys.argv[1:]` is used.

    Returns:
        Process exit code.
    """

    import argparse
    import sys

    parser = argparse.ArgumentParser(prog="laga")
    parser.add_argument("text", nargs="?", help="Text containing malformed JSON")
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read input from standard input",
    )
    parser.add_argument(
        "--strict", action="store_true", help="Reject ambiguous repairs"
    )
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print repaired JSON",
    )
    output_group.add_argument(
        "--compact",
        action="store_true",
        help="Force compact output",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=_MAX_NESTING_DEPTH,
        help="Maximum nesting depth to allow",
    )
    parser.add_argument(
        "--max-input-size",
        type=int,
        default=None,
        help="Reject inputs larger than this many characters",
    )
    parser.add_argument(
        "--duplicate-keys",
        choices=("last", "error"),
        default="last",
        help="Control how duplicate object keys are handled",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress normal output on success",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.stdin or args.text is None or args.text == "-":
        sample = sys.stdin.read()
    else:
        sample = args.text
    try:
        rendered = repair_to_str(
            sample,
            strict=args.strict,
            max_depth=args.max_depth,
            max_input_size=args.max_input_size,
            duplicate_keys=args.duplicate_keys,
            pretty=args.pretty,
        )
        if not args.quiet:
            print(rendered)
    except LagaError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


def _repair_text(
    text: str,
    *,
    strict: bool,
    max_depth: int = _MAX_NESTING_DEPTH,
    max_input_size: int | None = _MAX_INPUT_SIZE,
    duplicate_keys: DuplicateKeyPolicy = "last",
) -> Any:
    _check_input_size(text, max_input_size=max_input_size)
    normalized = _normalize_text(text)
    candidates = list(_candidate_texts(normalized))
    last_error: LagaError | None = None
    for candidate in candidates:
        try:
            tokens = _Tokenizer(candidate, strict=strict).tokenize()
            parser = _Parser(
                tokens,
                strict=strict,
                max_depth=max_depth,
                duplicate_keys=duplicate_keys,
            )
            return parser.parse()
        except LagaError as exc:
            last_error = _with_context(exc, candidate)
    if last_error is None:
        raise LagaError("No JSON value found", 0)
    if last_error.context is None and last_error.position is not None:
        raise LagaError(
            last_error.message,
            last_error.position,
            _context_snippet(text, last_error.position),
        )
    raise last_error


def _validate_limits(
    *,
    max_depth: int,
    max_input_size: int | None,
    duplicate_keys: DuplicateKeyPolicy,
) -> None:
    if max_depth < 1:
        raise ValueError("max_depth must be at least 1")
    if max_input_size is not None and max_input_size < 0:
        raise ValueError("max_input_size must be non-negative or None")
    if duplicate_keys not in {"last", "error"}:
        raise ValueError("duplicate_keys must be 'last' or 'error'")


def _check_input_size(text: str, *, max_input_size: int | None) -> None:
    if max_input_size is None:
        return
    if len(text) > max_input_size:
        raise LagaError(
            f"Input exceeds maximum size of {max_input_size} characters",
            max_input_size,
        )


def _with_context(error: LagaError, text: str) -> LagaError:
    if error.context is not None or error.position is None:
        return error
    return LagaError(
        error.message,
        error.position,
        _context_snippet(text, error.position),
    )


def _context_snippet(text: str, position: int, *, radius: int = 24) -> str:
    start = max(0, position - radius)
    end = min(len(text), position + radius)
    snippet = text[start:end].replace("\r", "\\r").replace("\n", "\\n")
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."
    return snippet


def _normalize_text(text: str) -> str:
    stripped = _extract_fenced_text(text)
    if stripped is None:
        stripped = text
    return stripped.translate(_SMART_QUOTES)


def _extract_fenced_text(text: str) -> str | None:
    fence_start = text.find("```")
    if fence_start == -1:
        return None
    line_end = text.find("\n", fence_start + 3)
    if line_end == -1:
        return text[fence_start + 3 :].strip()
    fence_end = text.find("```", line_end + 1)
    if fence_end == -1:
        return text[line_end + 1 :].strip()
    return text[line_end + 1 : fence_end].strip()


def _candidate_texts(text: str) -> Iterable[str]:
    if "```" in text:
        yield text
        return
    found = False
    for index, char in enumerate(text):
        if char in "[{":
            found = True
            yield _capture_balanced_region(text, index)
    if not found:
        yield text


def _capture_balanced_region(text: str, start: int) -> str:
    opening = text[start]
    closing = "]" if opening == "[" else "}"
    depth = 0
    in_string = False
    quote = ""
    escaped = False
    index = start
    while index < len(text):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                in_string = False
        else:
            if char in "\"'":
                in_string = True
                quote = char
            elif char == "/" and _next_char(text, index) == "/":
                index = _skip_line_comment(text, index + 2)
                continue
            elif char == "/" and _next_char(text, index) == "*":
                index = _skip_block_comment(text, index + 2)
                continue
            elif char == opening:
                depth += 1
            elif char == closing:
                depth -= 1
                if depth == 0:
                    return text[start : index + 1]
        index += 1
    return text[start:]


def _next_char(text: str, index: int) -> str | None:
    next_index = index + 1
    if next_index >= len(text):
        return None
    return text[next_index]


def _skip_line_comment(text: str, index: int) -> int:
    while index < len(text) and text[index] not in "\r\n":
        index += 1
    return index - 1


def _skip_block_comment(text: str, index: int) -> int:
    while index < len(text) - 1:
        if text[index] == "*" and text[index + 1] == "/":
            return index + 1
        index += 1
    return len(text) - 1


class _Parser:
    def __init__(
        self,
        tokens: list[_Token],
        *,
        strict: bool,
        max_depth: int = _MAX_NESTING_DEPTH,
        duplicate_keys: DuplicateKeyPolicy = "last",
    ) -> None:
        self._tokens = tokens
        self._strict = strict
        self._max_depth = max_depth
        self._duplicate_keys = duplicate_keys
        self._index = 0
        self._depth = 0

    def parse(self) -> Any:
        value = self._parse_value()
        if self._peek() is not None:
            token = self._peek()
            assert token is not None
            raise LagaError("Unexpected trailing content", token.position)
        return value

    def _parse_value(self) -> Any:
        token = self._peek()
        if token is None:
            raise LagaError("Expected JSON value", self._current_position())
        if token.kind == "LBRACE":
            return self._parse_object()
        if token.kind == "LBRACKET":
            return self._parse_array()
        if token.kind == "STRING":
            self._index += 1
            return token.value
        if token.kind == "NUMBER":
            self._index += 1
            try:
                return json.loads(token.value)
            except json.JSONDecodeError as exc:
                raise LagaError("Invalid number", token.position) from exc
        if token.kind == "IDENT":
            self._index += 1
            lowered = token.value.lower()
            if lowered in _LITERAL_MAP:
                return _LITERAL_MAP[lowered]
            raise LagaError("Unexpected identifier", token.position)
        raise LagaError("Expected JSON value", token.position)

    def _parse_object(self) -> dict[str, Any]:
        self._expect("LBRACE")
        self._enter_container()
        result: dict[str, Any] = {}
        try:
            if self._match("RBRACE"):
                return result
            while True:
                token = self._peek()
                if token is None:
                    if self._strict:
                        raise LagaError("Unterminated object", self._current_position())
                    return result
                if token.kind == "RBRACE":
                    self._index += 1
                    return result
                key = self._parse_key()
                self._expect("COLON")
                if key in result and self._duplicate_keys == "error":
                    raise LagaError("Duplicate key", token.position)
                result[key] = self._parse_value()
                token = self._peek()
                if token is None:
                    if self._strict:
                        raise LagaError("Unterminated object", self._current_position())
                    return result
                if token.kind == "COMMA":
                    self._index += 1
                    if self._match("RBRACE"):
                        return result
                    continue
                if token.kind == "RBRACE":
                    self._index += 1
                    return result
                if self._begins_member(token):
                    if self._strict:
                        raise LagaError(
                            "Missing comma between object members", token.position
                        )
                    continue
                raise LagaError("Expected comma or closing brace", token.position)
        finally:
            self._exit_container()

    def _parse_array(self) -> list[Any]:
        self._expect("LBRACKET")
        self._enter_container()
        result: list[Any] = []
        try:
            if self._match("RBRACKET"):
                return result
            while True:
                token = self._peek()
                if token is None:
                    if self._strict:
                        raise LagaError("Unterminated array", self._current_position())
                    return result
                if token.kind == "RBRACKET":
                    self._index += 1
                    return result
                result.append(self._parse_value())
                token = self._peek()
                if token is None:
                    if self._strict:
                        raise LagaError("Unterminated array", self._current_position())
                    return result
                if token.kind == "COMMA":
                    self._index += 1
                    if self._match("RBRACKET"):
                        return result
                    continue
                if token.kind == "RBRACKET":
                    self._index += 1
                    return result
                if self._begins_value(token):
                    if self._strict:
                        raise LagaError(
                            "Missing comma between array items", token.position
                        )
                    continue
                raise LagaError("Expected comma or closing bracket", token.position)
        finally:
            self._exit_container()

    def _parse_key(self) -> str:
        token = self._peek()
        if token is None:
            raise LagaError("Expected object key", self._current_position())
        if token.kind == "STRING":
            self._index += 1
            return token.value
        if token.kind == "IDENT":
            self._index += 1
            return token.value
        raise LagaError("Expected object key", token.position)

    def _expect(self, kind: str) -> _Token:
        token = self._peek()
        if token is None or token.kind != kind:
            position = self._current_position() if token is None else token.position
            raise LagaError(f"Expected {kind.lower()}", position)
        self._index += 1
        return token

    def _match(self, kind: str) -> bool:
        token = self._peek()
        if token is None or token.kind != kind:
            return False
        self._index += 1
        return True

    def _peek(self) -> _Token | None:
        if self._index >= len(self._tokens):
            return None
        return self._tokens[self._index]

    def _current_position(self) -> int:
        token = self._peek()
        if token is not None:
            return token.position
        if not self._tokens:
            return 0
        return self._tokens[-1].position + len(self._tokens[-1].value)

    def _begins_value(self, token: _Token) -> bool:
        return token.kind in {"LBRACE", "LBRACKET", "STRING", "NUMBER", "IDENT"}

    def _begins_member(self, token: _Token) -> bool:
        return token.kind in {"STRING", "IDENT"}

    def _enter_container(self) -> None:
        self._depth += 1
        if self._depth > self._max_depth:
            raise LagaError("JSON is too deeply nested", self._current_position())

    def _exit_container(self) -> None:
        self._depth -= 1
