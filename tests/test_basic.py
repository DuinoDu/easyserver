import easyserver


def test_version():
    version = easyserver.__version__
    assert version
