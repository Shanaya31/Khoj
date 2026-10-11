import pytest
from app.llm import LLMError, parse_json_object


def test_parses_plain_json():
    assert parse_json_object('{"a": 1}') == {"a": 1}


def test_extracts_json_from_chatty_output():
    assert parse_json_object('Sure! ```json\n{"a": 1}\n``` hope that helps') == {"a": 1}


@pytest.mark.parametrize("bad", ["no json here", "[1, 2]", '{"a": ', ""])
def test_rejects_unusable_output(bad):
    with pytest.raises(LLMError):
        parse_json_object(bad)
