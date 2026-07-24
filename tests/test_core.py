from __future__ import annotations

import json

import pytest

import laga
from laga import core
from laga.errors import LagaError


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ('{"a": 1,}', {"a": 1}),
        ('{"a": 1 "b": 2}', {"a": 1, "b": 2}),
        ("{'a': 'b'}", {"a": "b"}),
        ('{name: "Ada"}', {"name": "Ada"}),
        (
            '{"ok": True, "none": None, "bad": False}',
            {"ok": True, "none": None, "bad": False},
        ),
        ('{"a": 1 // note\n}', {"a": 1}),
        ('{"a": 1 /* note */}', {"a": 1}),
        ('```json\n{"a": 1}\n```', {"a": 1}),
        ('Result: {"a": 1}', {"a": 1}),
        ('{"a": [1, 2, 3', {"a": [1, 2, 3]}),
        ('{"quote": “hi”}', {"quote": "hi"}),
        ('{"nested": {"a": 1, "b": [2, 3,]}}', {"nested": {"a": 1, "b": [2, 3]}}),
    ],
)
def test_repair_rules(text: str, expected: object) -> None:
    assert laga.repair(text) == expected


def test_repair_to_str_normalizes_output() -> None:
    text = "{name: 'Ada', roles: ['admin',], active: True}"
    assert laga.repair_to_str(text) == '{"name":"Ada","roles":["admin"],"active":true}'


def test_loads_is_alias() -> None:
    text = '{"a": 1}'
    assert laga.loads(text) == {"a": 1}
    assert laga.loads is laga.repair


def test_valid_json_uses_fast_path(monkeypatch: pytest.MonkeyPatch) -> None:
    called = {"value": False}
    stdlib_loads = json.loads

    def fake_loads(text: str) -> object:
        called["value"] = True
        return stdlib_loads(text)

    def fail(*args: object, **kwargs: object) -> object:
        raise AssertionError("repair path should not be used for valid JSON")

    monkeypatch.setattr(core.json, "loads", fake_loads)
    monkeypatch.setattr(core, "_repair_text", fail)
    assert laga.repair('{"a": 1}') == {"a": 1}
    assert called["value"] is True


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ('{"a": 1 "b": 2}', "Missing comma between object members"),
        ('{"a": [1 2]}', "Missing comma between array items"),
        ('{"a": 1', "Unterminated object"),
        ("[1, 2", "Unterminated array"),
    ],
)
def test_strict_mode_rejects_ambiguous_repairs(text: str, message: str) -> None:
    with pytest.raises(LagaError, match=message):
        laga.repair(text, strict=True)


def test_unrecoverable_input_raises_laga_error() -> None:
    with pytest.raises(LagaError, match="Unexpected identifier"):
        laga.repair("not json at all")


def test_duplicate_keys_use_last_value() -> None:
    assert laga.repair('{"a": 1, "a": 2}') == {"a": 2}


def test_deeply_nested_input_is_rejected() -> None:
    text = "[" * 260 + "0" + "]" * 260
    with pytest.raises(LagaError, match="too deeply nested"):
        tokens = core._Tokenizer(text, strict=False).tokenize()
        core._Parser(tokens, strict=False).parse()
