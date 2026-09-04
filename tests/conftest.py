import pytest

import wmbench
from environment import warning_filters


@pytest.fixture(autouse=True)
def strict_warnings():
    warning_filters.apply()
