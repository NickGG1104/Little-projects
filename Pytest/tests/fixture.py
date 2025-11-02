import pytest


@pytest.fixture()
def test_lst():
    return ['Hello! ', 'World!!']


@pytest.fixture()
def test_dict():
    return {'a': 1, 'b': 2}
