import pytest
import tkinter as tk
from system_monitor import  root, write_en, stop, check, is_valid, page_loading, proc_label
import system_monitor

@pytest.fixture
def app():
    root_test = system_monitor.Tk()
    return root_test

def test_page_loading():
    assert write_en is False
    assert stop is False
    assert check == 0

def test_valid():
    assert is_valid(newval="12") is True
    assert is_valid(newval="ABC") is False

def test_page(app):

    assert proc_label(app)['text'] == ""


print(proc_label)
pytest.main()
