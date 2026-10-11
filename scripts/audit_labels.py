# SPDX-License-Identifier: Apache-2.0
"""Verify the authorised release asset and inspect its schema without scoring."""

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/labels/training_data.tsv"
SIZE = 64_412_996
SHA256 = "19a9f888f06655e17e95c7110ab4ff5ace38ece121e6cb1ac3bcb7d3c087abcc"
TRAITS = {
    "temperature_optimum": "use_temperature",
    "oxygen": "use_oxygen",
    "salinity_optimum": "use_salinity",
    "ph_optimum": "use_ph",
}


def main() -> None:
    if RAW.stat().st_size != SIZE:
        raise SystemExit("Stop: release asset size mismatch")
    with RAW.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if digest != SHA256:
        raise SystemExit("Stop: release asset checksum mismatch")
    counts = {
        trait: {"nonmissing": 0, "missing": 0, "upstream_use_true": 0,
                "upstream_use_false": 0, "upstream_flag_other": 0}
        for trait in TRAITS
    }
    accessions: Counter[str] = Counter()
    oxygen_values: Counter[str] = Counter()
    with RAW.open(newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        columns = reader.fieldnames
        if columns is None or len(columns) != 267:
            raise SystemExit("Stop: unexpected table schema")
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise SystemExit("Stop: malformed table row")
            accessions[row[columns[0]]] += 1
            for trait, flag in TRAITS.items():
                present = row[trait].strip().lower() not in {"", "nan", "na", "none"}
                counts[trait]["nonmissing" if present else "missing"] += 1
                flag_value = row[flag].strip().lower()
                key = {"true": "upstream_use_true", "false": "upstream_use_false"}.get(
                    flag_value, "upstream_flag_other"
                )
                counts[trait][key] += 1
            if row["oxygen"]:
                oxygen_values[row["oxygen"]] += 1
    result = {
        "status": "sources_accepted_feature_verification_pending",
        "bytes": SIZE,
        "sha256": digest,
        "rows": accessions.total(),
        "unique_accessions": len(accessions),
        "duplicated_accessions": sum(count > 1 for count in accessions.values()),
        "blank_accessions": accessions[""],
        "trait_inspection_counts": counts,
        "oxygen_value_counts": dict(sorted(oxygen_values.items())),
        "analysis_exclusions": None,
        "analysis_exclusions_reason": "GTDB mapping pending verified feature sample",
        "column_count_including_accession": len(columns),
        "column_sources": {
            "accession_from_bacdive": columns[:1],
            "ncbi_sequence_derived_features": columns[1:231],
            "bacdive_traits_and_derived_flags": columns[231:260],
            "gtdb_taxonomy_fields": columns[260:],
        },
        "outer_fold_predictions_or_metrics_computed": False,
    }
    output = ROOT / "data/gtdb-derived/label-audit.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items()
                      if key != "column_sources"}, indent=2))


if __name__ == "__main__":
    main()
