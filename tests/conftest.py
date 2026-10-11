# SPDX-License-Identifier: Apache-2.0
"""Offline fixtures reject attempts to open a network socket."""
from collections.abc import Iterator
from typing import Any
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def no_network() -> Iterator[None]:
    def refuse(*args: Any, **kwargs: Any) -> None:
        raise AssertionError('Offline fixture attempted network access')
    with patch('socket.socket.connect', refuse), patch('socket.socket.connect_ex', refuse):
        yield
