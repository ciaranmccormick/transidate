from pathlib import Path

import pytest

DATA_DIR = Path(__file__).parent.joinpath("data")


@pytest.fixture
def txc21():
    filepath = str(DATA_DIR.joinpath("txc21good.xml"))
    with open(filepath, "r") as f_:
        yield f_


@pytest.fixture
def txc24():
    filepath = str(DATA_DIR.joinpath("txc24good.xml"))
    with open(filepath, "r") as f_:
        yield f_


@pytest.fixture
def txc24invalid():
    filepath = str(DATA_DIR.joinpath("txc24bad.xml"))
    with open(filepath, "r") as f_:
        yield f_


@pytest.fixture
def txc24_zip():
    filepath = str(DATA_DIR.joinpath("txc24archive.zip"))
    with open(filepath, "rb") as f_:
        yield f_


@pytest.fixture
def netex():
    filepath = str(DATA_DIR.joinpath("netex1good.xml"))
    with open(filepath, "r") as f_:
        yield f_


@pytest.fixture
def siri2():
    filepath = str(DATA_DIR.joinpath("sirivm2good.xml"))
    with open(filepath, "r") as f_:
        yield f_
