# tests/test_import.py
import importlib.util


def test_import():
    """
    A simple test to ensure the despanol package can be imported.
    """
    spec = importlib.util.find_spec("despanol")
    assert spec is not None, "Failed to find the despanol package"
