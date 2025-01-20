import pytest
from nw_sys_mon import write_en, stop, check, is_valid


def test_page_loading():
    assert write_en is False
    assert stop is False
    assert check == 0


def test_valid():
    assert is_valid("12") is True
    assert is_valid("+1234") is False
    assert is_valid("999") is True
    assert is_valid("ABC") is False


pytest.main()
