import pytest
from src.main import say_hello

def test_say_hello_default():
    assert say_hello("World") == "Hello, World"

def test_say_hello_custom_name():
    assert say_hello("Alice") == "Hello, Alice"
