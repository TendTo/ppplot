from importlib.metadata import version


def test_version():
    assert version("ppplot") == "0.1.0"
