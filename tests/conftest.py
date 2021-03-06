from pathlib import Path

import pytest
from transidate.datasets import DataSet

DATA_DIR = Path(__file__).parent.joinpath("data")


@pytest.fixture
def txc21():
    filepath = DATA_DIR / "txc21good.xml"
    return DataSet(filepath)


@pytest.fixture
def txc24():
    filepath = DATA_DIR / "txc24good.xml"
    return DataSet(filepath)


@pytest.fixture
def txc24invalid():
    filepath = DATA_DIR / "txc24bad.xml"
    return DataSet(filepath)


@pytest.fixture
def txc24_archive():
    filepath = DATA_DIR.joinpath("txc24archive.zip")
    return DataSet(filepath)


@pytest.fixture
def txc21_archive():
    filepath = DATA_DIR.joinpath("txc21archive.zip")
    return DataSet(filepath)


@pytest.fixture
def netex():
    filepath = DATA_DIR / "netex110.xml"
    return DataSet(filepath)


@pytest.fixture
def siri2():
    filepath = DATA_DIR / "sirivm2good.xml"
    return DataSet(filepath)
