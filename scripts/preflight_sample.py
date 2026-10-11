# SPDX-License-Identifier: Apache-2.0
"""Resolve the fixed verification sample and estimate all sequence bytes first."""

import json
import re
import shutil
import time
import urllib.error
import urllib.request
from urllib.parse import quote
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/verification"
LIMIT = 8_000_000_000


def assembly_basename(accession: str, assembly_name: str) -> str:
    """NCBI directory names replace punctuation and whitespace with underscores."""
    return accession + "_" + re.sub(r"[^A-Za-z0-9._-]", "_", assembly_name)


def check_space() -> None:
    if shutil.disk_usage("/").free < 25_000_000_000:
        raise SystemExit("Stop: free space below 25 GB")


def gate_status(total_bytes: int, errors: list[dict[str, str]]) -> str:
    """Missing source sizes cannot be treated as a passing estimate."""
    if errors:
        return "size_unknown"
    return "size_gate_exceeded" if total_bytes > LIMIT else "size_gate_passed"


def main() -> None:
    check_space()
    sample = json.loads((RAW / "sample.json").read_text())
    reports = json.loads((RAW / "assembly-reports.json").read_text())["reports"]
    by_accession = {r["accession"].split(".")[0]: r for r in reports}
    previous = RAW / "sequence-preflight.json"
    state = json.loads(previous.read_text()) if previous.exists() else {}
    records: list[dict[str, Any]] = state.get("records", [])
    errors: list[dict[str, str]] = state.get("errors", [])
    attempted = {r["url"] for r in records + errors if "url" in r}
    result: dict[str, Any] = {}
    for number, accession in enumerate(sample["accessions"], 1):
        report = by_accession.get(accession)
        if report is None:
            errors.append({"accession": accession, "reason": "No assembly report"})
            continue
        resolved = report["accession"]
        digits = resolved[4:13]
        basename = assembly_basename(resolved, report["assembly_info"]["assembly_name"])
        directory = "/".join((digits[:3], digits[3:6], digits[6:]))
        base = f"https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/{directory}/{basename}"
        for suffix in ("_protein.faa.gz", "_genomic.fna.gz"):
            url = quote(f"{base}/{basename}{suffix}", safe=":/")
            if url in attempted:
                continue
            time.sleep(1.0)
            try:
                with urllib.request.urlopen(
                    urllib.request.Request(url, method="HEAD"), timeout=60
                ) as response:
                    size = int(response.headers["Content-Length"])
                    records.append({
                        "accession": accession,
                        "resolved_accession": resolved,
                        "url": url,
                        "path": f"data/raw/verification/sequences/{basename}{suffix}",
                        "bytes": size,
                        "last_modified": response.headers.get("Last-Modified"),
                    })
            except (urllib.error.URLError, ValueError, KeyError) as error:
                errors.append({"accession": accession, "url": url, "reason": str(error)})
        result = {
            "status": "estimating", "records": records, "errors": errors,
            "total_sequence_bytes": sum(r["bytes"] for r in records),
            "limit_bytes": LIMIT, "request_spacing_seconds": 1.0,
        }
        (RAW / "sequence-preflight.json").write_text(json.dumps(result, indent=2) + "\n")
        if number % 10 == 0:
            print(f"Estimated {number}/100 genomes; errors={len(errors)}", flush=True)
        check_space()
    result["status"] = gate_status(result["total_sequence_bytes"], errors)
    (RAW / "sequence-preflight.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "records"}, indent=2))
    if result["status"] != "size_gate_passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
