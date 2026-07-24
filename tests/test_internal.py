from __future__ import annotations

import sys
from io import StringIO

import pytest

from laga import core
from laga.errors import LagaError
from laga.tokenizer import (
    _is_hex_digit,
    _is_identifier_part,
    _is_identifier_start,
    _Token,
    _Tokenizer,
)


def test_normalize_text_strips_fences_and_smart_quotes() -> None:
    text = """Intro
```json
{\u201cname\u201d: \u2018Ada\u2019}
```
"""
    assert core._normalize_text(text) == "{\"name\": 'Ada'}"


def test_extract_fenced_text_handles_missing_fence() -> None:
    assert core._extract_fenced_text("plain text") is None
    assert core._extract_fenced_text('```json\n{"a":1}\n```') == '{"a":1}'


def test_candidate_texts_preserves_fenced_text() -> None:
    fenced = '```json\n{"a":1}\n```'
    assert list(core._candidate_texts(fenced)) == [fenced]


def test_candidate_texts_choose_balanced_slices() -> None:
    assert list(core._candidate_texts("plain text")) == ["plain text"]
    assert list(core._candidate_texts('before {"a": 1} after')) == ['{"a": 1}']


def test_capture_balanced_region_handles_comments_and_strings() -> None:
    text = '{"a": "{not a brace}", /* comment */ "b": [1, 2]}'
    assert core._capture_balanced_region(text, 0) == text


def test_comment_skipping_helpers() -> None:
    assert core._next_char("abc", 0) == "b"
    assert core._next_char("a", 0) is None
    assert core._skip_line_comment("// note\n{}", 2) == 6
    assert core._skip_block_comment("/* note */{}", 2) == 9


def test_repair_text_tries_multiple_candidates() -> None:
    text = 'noise {not json} and then {"a": 1}'
    assert core._repair_text(text, strict=False) == {"a": 1}


def test_repair_text_reports_missing_candidates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(core, "_candidate_texts", lambda text: [])
    with pytest.raises(LagaError, match="No JSON value found"):
        core._repair_text("", strict=False)


def test_main_cli_success_and_failure(capsys: pytest.CaptureFixture[str]) -> None:
    old_stdin = sys.stdin
    sys.stdin = StringIO('{"stdin": 1}')
    try:
        assert core.main([]) == 0
    finally:
        sys.stdin = old_stdin
    assert core.main(['{"a": 1}']) == 0
    assert core.main(["not json at all"]) == 1
    output = capsys.readouterr()
    assert '{"a":1}' in output.out
    assert "Unexpected identifier" in output.err


def test_parser_trailing_content_and_invalid_number() -> None:
    parser = core._Parser(
        [_Token("NUMBER", "1", 0), _Token("NUMBER", "2", 1)], strict=False
    )
    with pytest.raises(LagaError, match="Unexpected trailing content"):
        parser.parse()

    parser = core._Parser([_Token("NUMBER", "1e", 0)], strict=False)
    with pytest.raises(LagaError, match="Invalid number"):
        parser.parse()


def test_parser_empty_containers_and_expect_helpers() -> None:
    object_parser = core._Parser(
        [_Token("LBRACE", "{", 0), _Token("RBRACE", "}", 1)], strict=False
    )
    array_parser = core._Parser(
        [_Token("LBRACKET", "[", 0), _Token("RBRACKET", "]", 1)], strict=False
    )
    assert object_parser.parse() == {}
    assert array_parser.parse() == []

    assert core._Parser([], strict=False)._current_position() == 0

    with pytest.raises(LagaError, match="Expected JSON value"):
        core._Parser([], strict=False).parse()

    with pytest.raises(LagaError, match="Expected JSON value"):
        core._Parser([_Token("BOGUS", "x", 4)], strict=False).parse()

    with pytest.raises(LagaError, match="Expected comma or closing brace"):
        core._Parser(
            [
                _Token("LBRACE", "{", 0),
                _Token("STRING", "key", 1),
                _Token("COLON", ":", 2),
                _Token("STRING", "value", 3),
                _Token("NUMBER", "1", 4),
            ],
            strict=False,
        ).parse()

    with pytest.raises(LagaError, match="Expected comma or closing bracket"):
        core._Parser(
            [
                _Token("LBRACKET", "[", 0),
                _Token("NUMBER", "1", 1),
                _Token("COLON", ":", 2),
            ],
            strict=False,
        ).parse()

    with pytest.raises(LagaError, match="Expected object key"):
        core._Parser(
            [
                _Token("LBRACE", "{", 0),
                _Token("NUMBER", "1", 1),
            ],
            strict=False,
        )._parse_key()

    parser = core._Parser([_Token("STRING", "x", 3)], strict=False)
    with pytest.raises(LagaError, match="Expected lbrace"):
        parser._expect("LBRACE")
    assert parser._current_position() == 3
    assert parser._begins_value(_Token("IDENT", "true", 0)) is True
    assert parser._begins_member(_Token("STRING", "k", 0)) is True


def test_tokenizer_handles_comments_strings_numbers_and_literals() -> None:
    text = (
        "// lead\n"
        "{key: 'A\\n\\u0042', value: -1.5e+2, "
        "flag: False, none: None, tail: /* x */ 3}"
    )
    tokens = _Tokenizer(text, strict=False).tokenize()
    kinds = [token.kind for token in tokens]
    assert kinds == [
        "LBRACE",
        "IDENT",
        "COLON",
        "STRING",
        "COMMA",
        "IDENT",
        "COLON",
        "NUMBER",
        "COMMA",
        "IDENT",
        "COLON",
        "IDENT",
        "COMMA",
        "IDENT",
        "COLON",
        "IDENT",
        "COMMA",
        "IDENT",
        "COLON",
        "NUMBER",
        "RBRACE",
    ]
    assert tokens[3].value == "A\nB"


@pytest.mark.parametrize(
    ("escape", "expected"),
    [
        ('\\"', '"'),
        ("\\\\", "\\"),
        ("\\/", "/"),
        ("\\b", "\b"),
        ("\\f", "\f"),
        ("\\r", "\r"),
        ("\\t", "\t"),
        ("\\u0041", "A"),
    ],
)
def test_tokenizer_supported_escapes(escape: str, expected: str) -> None:
    assert _Tokenizer(f'"{escape}"', strict=True).tokenize() == [
        _Token("STRING", expected, 0)
    ]


def test_tokenizer_number_edges_and_peek_helpers() -> None:
    assert _Tokenizer("0", strict=True).tokenize() == [_Token("NUMBER", "0", 0)]
    with pytest.raises(LagaError, match="Incomplete number"):
        _Tokenizer("-", strict=True).tokenize()
    with pytest.raises(LagaError, match="Invalid number"):
        _Tokenizer("-x", strict=True).tokenize()
    assert _Tokenizer("1e-2", strict=True).tokenize() == [_Token("NUMBER", "1e-2", 0)]
    assert _Tokenizer("a", strict=False)._peek_char(1) is None


def test_tokenizer_incomplete_escape_and_unterminated_number() -> None:
    unterminated = '"' + "\\"
    assert _Tokenizer(unterminated, strict=False).tokenize() == [
        _Token("STRING", "\\", 0)
    ]
    with pytest.raises(LagaError, match="Incomplete escape sequence"):
        _Tokenizer(unterminated, strict=True).tokenize()
    with pytest.raises(LagaError, match="Invalid number"):
        _Tokenizer("1.", strict=True).tokenize()
    with pytest.raises(LagaError, match="Invalid number"):
        _Tokenizer("1e+", strict=True).tokenize()


def test_non_strict_unicode_escape_and_block_comment_fallthrough() -> None:
    assert _Tokenizer('"\\u12"', strict=False).tokenize()[0].value.startswith("u")
    assert _Tokenizer("/* note", strict=False).tokenize() == []


def test_tokenizer_strict_unicode_escape_error() -> None:
    with pytest.raises(LagaError, match="Invalid unicode escape"):
        _Tokenizer('"\\u12"', strict=True).tokenize()


def test_tokenizer_strict_string_and_comment_errors() -> None:
    with pytest.raises(LagaError, match="Unterminated string literal"):
        _Tokenizer("'abc", strict=True).tokenize()
    with pytest.raises(LagaError, match="Invalid escape sequence"):
        _Tokenizer("'\\q'", strict=True).tokenize()
    with pytest.raises(LagaError, match="Unterminated block comment"):
        _Tokenizer("/* comment", strict=True).tokenize()


def test_tokenizer_non_strict_string_recovery() -> None:
    tokens = _Tokenizer("'abc", strict=False).tokenize()
    assert tokens == [_Token("STRING", "abc", 0)]
    assert _Tokenizer("'\\q'", strict=False).tokenize() == [_Token("STRING", "q", 0)]


def test_identifier_helpers_and_unexpected_character() -> None:
    assert _is_identifier_start("_") is True
    assert _is_identifier_start("a") is True
    assert _is_identifier_part("$") is True
    assert _is_identifier_part("1") is True
    assert _is_hex_digit("f") is True
    assert _is_hex_digit("9") is True
    with pytest.raises(LagaError, match="Unexpected character"):
        _Tokenizer("@", strict=False).tokenize()


def test_balanced_region_handles_line_comments_and_escapes() -> None:
    text = '{"a": "\\\\", // note\n "b": 1}'
    assert core._capture_balanced_region(text, 0) == text


def test_laga_error_formats_position() -> None:
    assert str(LagaError("problem")) == "problem"
    assert str(LagaError("problem", position=7)) == "problem at position 7"
