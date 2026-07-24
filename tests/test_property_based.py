from __future__ import annotations

import json

from hypothesis import given, settings
from hypothesis import strategies as st

import laga

json_scalars = (
    st.none()
    | st.booleans()
    | st.integers()
    | st.floats(allow_nan=False, allow_infinity=False)
    | st.text()
)
json_values = st.recursive(
    json_scalars,
    lambda children: (
        st.lists(children, max_size=5)
        | st.dictionaries(st.text(min_size=1, max_size=8), children, max_size=5)
    ),
    max_leaves=25,
)


@given(json_values)
@settings(max_examples=100, deadline=None)
def test_valid_json_survives_round_trip(value: object) -> None:
    text = json.dumps(value, ensure_ascii=False)
    assert laga.repair(text) == json.loads(text)
    assert json.loads(laga.repair_to_str(text)) == json.loads(text)
