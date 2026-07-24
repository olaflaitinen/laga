from __future__ import annotations

import laga


def test_llm_style_object_with_multiple_issues() -> None:
    text = """Sure, here is the JSON you asked for:
```json
{
  name: “Ada Lovelace”,
  title: 'Analyst',
  active: True,
  projects: [
    {id: 1, name: 'Computation',},
    {id: 2, name: 'Notes'}
  ]
}
```
"""
    expected = {
        "name": "Ada Lovelace",
        "title": "Analyst",
        "active": True,
        "projects": [
            {"id": 1, "name": "Computation"},
            {"id": 2, "name": "Notes"},
        ],
    }
    assert laga.repair(text) == expected


def test_truncated_nested_structure() -> None:
    text = '{"response": {"items": [1, 2, 3], "meta": {"count": 3}'
    expected = {"response": {"items": [1, 2, 3], "meta": {"count": 3}}}
    assert laga.repair(text) == expected


def test_comments_and_missing_commas_in_config_style_text() -> None:
    text = """
    {
      // service settings
      host: "localhost"
      port: 8080,
      use_tls: False /* local only */
    }
    """
    assert laga.repair(text) == {"host": "localhost", "port": 8080, "use_tls": False}
