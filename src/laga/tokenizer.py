from __future__ import annotations

from dataclasses import dataclass

from .errors import LagaError


@dataclass(frozen=True, slots=True)
class _Token:
    kind: str
    value: str
    position: int


class _Tokenizer:
    def __init__(self, text: str, *, strict: bool) -> None:
        self._text = text
        self._strict = strict
        self._index = 0
        self._length = len(text)

    def tokenize(self) -> list[_Token]:
        tokens: list[_Token] = []
        while self._index < self._length:
            char = self._text[self._index]
            if char.isspace():
                self._index += 1
                continue
            if char == "/" and self._peek_char(1) == "/":
                self._skip_line_comment()
                continue
            if char == "/" and self._peek_char(1) == "*":
                self._skip_block_comment()
                continue
            if char == "{":
                tokens.append(_Token("LBRACE", char, self._index))
                self._index += 1
                continue
            if char == "}":
                tokens.append(_Token("RBRACE", char, self._index))
                self._index += 1
                continue
            if char == "[":
                tokens.append(_Token("LBRACKET", char, self._index))
                self._index += 1
                continue
            if char == "]":
                tokens.append(_Token("RBRACKET", char, self._index))
                self._index += 1
                continue
            if char == ":":
                tokens.append(_Token("COLON", char, self._index))
                self._index += 1
                continue
            if char == ",":
                tokens.append(_Token("COMMA", char, self._index))
                self._index += 1
                continue
            if char in "\"'":
                tokens.append(self._consume_string(char))
                continue
            if char == "-" or char.isdigit():
                tokens.append(self._consume_number())
                continue
            if _is_identifier_start(char):
                tokens.append(self._consume_identifier())
                continue
            raise LagaError(f"Unexpected character {char!r}", self._index)
        return tokens

    def _peek_char(self, offset: int) -> str | None:
        index = self._index + offset
        if index >= self._length:
            return None
        return self._text[index]

    def _skip_line_comment(self) -> None:
        self._index += 2
        while self._index < self._length and self._text[self._index] not in "\r\n":
            self._index += 1

    def _skip_block_comment(self) -> None:
        self._index += 2
        while self._index < self._length - 1:
            if self._text[self._index] == "*" and self._text[self._index + 1] == "/":
                self._index += 2
                return
            self._index += 1
        if self._strict:
            raise LagaError("Unterminated block comment", self._index)
        self._index = self._length

    def _consume_string(self, quote: str) -> _Token:
        start = self._index
        self._index += 1
        pieces: list[str] = []
        while self._index < self._length:
            char = self._text[self._index]
            self._index += 1
            if char == quote:
                return _Token("STRING", "".join(pieces), start)
            if char == "\\":
                pieces.append(self._consume_escape(start))
                continue
            pieces.append(char)
        if self._strict:
            raise LagaError("Unterminated string literal", start)
        return _Token("STRING", "".join(pieces), start)

    def _consume_escape(self, string_start: int) -> str:
        if self._index >= self._length:
            if self._strict:
                raise LagaError("Incomplete escape sequence", string_start)
            return "\\"
        char = self._text[self._index]
        self._index += 1
        if char in '"\\/':
            return char
        if char == "b":
            return "\b"
        if char == "f":
            return "\f"
        if char == "n":
            return "\n"
        if char == "r":
            return "\r"
        if char == "t":
            return "\t"
        if char == "u":
            return self._consume_unicode_escape(string_start)
        if self._strict:
            raise LagaError(f"Invalid escape sequence \\{char}", string_start)
        return char

    def _consume_unicode_escape(self, string_start: int) -> str:
        digits = self._text[self._index : self._index + 4]
        if len(digits) == 4 and all(_is_hex_digit(char) for char in digits):
            self._index += 4
            return chr(int(digits, 16))
        if self._strict:
            raise LagaError("Invalid unicode escape", string_start)
        return "u"

    def _consume_number(self) -> _Token:
        start = self._index
        if self._text[self._index] == "-":
            self._index += 1
        if self._index >= self._length:
            raise LagaError("Incomplete number", start)
        if self._text[self._index] == "0":
            self._index += 1
        else:
            if not self._text[self._index].isdigit():
                raise LagaError("Invalid number", start)
            while self._index < self._length and self._text[self._index].isdigit():
                self._index += 1
        if self._index < self._length and self._text[self._index] == ".":
            self._index += 1
            if self._index >= self._length or not self._text[self._index].isdigit():
                raise LagaError("Invalid number", start)
            while self._index < self._length and self._text[self._index].isdigit():
                self._index += 1
        if self._index < self._length and self._text[self._index] in "eE":
            self._index += 1
            if self._index < self._length and self._text[self._index] in "+-":
                self._index += 1
            if self._index >= self._length or not self._text[self._index].isdigit():
                raise LagaError("Invalid number", start)
            while self._index < self._length and self._text[self._index].isdigit():
                self._index += 1
        return _Token("NUMBER", self._text[start : self._index], start)

    def _consume_identifier(self) -> _Token:
        start = self._index
        self._index += 1
        while self._index < self._length and _is_identifier_part(
            self._text[self._index]
        ):
            self._index += 1
        return _Token("IDENT", self._text[start : self._index], start)


def _is_hex_digit(char: str) -> bool:
    return char.isdigit() or char.lower() in "abcdef"


def _is_identifier_start(char: str) -> bool:
    return char == "_" or char.isalpha()


def _is_identifier_part(char: str) -> bool:
    return char == "_" or char.isalpha() or char.isdigit() or char == "$"
