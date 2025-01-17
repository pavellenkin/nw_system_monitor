import pytest
from nw_sys_mon import write_en, stop, check, is_valid
import nw_sys_mon


@pytest.fixture
def app():
    root_test = nw_sys_mon.Tk()
    return root_test


def test_page_loading():
    assert write_en is False
    assert stop is False
    assert check == 0


def test_valid():
    assert is_valid(newval="12") is True
    assert is_valid(newval="ABC") is False


print(nw_sys_mon)
pytest.main()
