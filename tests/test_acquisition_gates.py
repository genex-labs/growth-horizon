# SPDX-License-Identifier: Apache-2.0
"""Offline tests of acquisition gates before any sequence download."""

import shutil
from unittest.mock import patch

import pytest

from scripts.preflight_sample import LIMIT, assembly_basename, check_space, gate_status


def test_ncbi_assembly_path_punctuation() -> None:
    assert assembly_basename("GCA_001053095.1", "5139_1#3") == "GCA_001053095.1_5139_1_3"
    assert assembly_basename("GCA_900103275.1", "IMG-taxon 2617270936 annotated assembly") == (
        "GCA_900103275.1_IMG-taxon_2617270936_annotated_assembly"
    )


def test_missing_file_prevents_passing_a_small_estimate() -> None:
    assert gate_status(123, [{"reason": "HTTP 404"}]) == "size_unknown"


def test_size_limit_boundary() -> None:
    assert gate_status(LIMIT, []) == "size_gate_passed"
    assert gate_status(LIMIT + 1, []) == "size_gate_exceeded"


def test_disk_space_stop_boundary() -> None:
    usage = shutil._ntuple_diskusage(100_000_000_000, 75_000_000_001, 24_999_999_999)
    with patch("scripts.preflight_sample.shutil.disk_usage", return_value=usage):
        with pytest.raises(SystemExit, match="below 25 GB"):
            check_space()
    usage = shutil._ntuple_diskusage(100_000_000_000, 75_000_000_000, 25_000_000_000)
    with patch("scripts.preflight_sample.shutil.disk_usage", return_value=usage):
        check_space()
