from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Sequence

from .engine import QueryMeasurement


def export_json(measurements: Sequence[QueryMeasurement], path: Path) -> None:
    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [measurement.to_dict() for measurement in measurements]
    path.write_text(json.dumps(payload, indent=2))


def export_csv(measurements: Sequence[QueryMeasurement], path: Path) -> None:
    if not measurements:
        return
    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [measurement.to_dict() for measurement in measurements]
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
