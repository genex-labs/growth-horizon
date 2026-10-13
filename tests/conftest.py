# SPDX-License-Identifier: Apache-2.0
"""Offline fixtures reject attempts to open a network socket."""
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest


def pytest_configure(config: pytest.Config) -> None:
    # pytest creates --basetemp itself but not its parent; work-tmp.noindex/ is
    # ignored by git, so a fresh clone needs the parent made here.
    basetemp = config.option.basetemp
    if basetemp:
        Path(basetemp).parent.mkdir(parents=True, exist_ok=True)


@pytest.fixture(autouse=True)
def no_network() -> Iterator[None]:
    def refuse(*args: Any, **kwargs: Any) -> None:
        raise AssertionError('Offline fixture attempted network access')
    with patch('socket.socket.connect', refuse), patch('socket.socket.connect_ex', refuse):
        yield
