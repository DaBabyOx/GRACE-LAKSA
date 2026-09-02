#!/usr/bin/env python3
"""Verify the public aggregate results without accessing complaint data."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
ALLOWED = {
    ".gitignore",
    "README.md",
    "SOURCES.sha256",
    "verify.py",
    "results/ablations.csv",
    "results/cross_source.csv",
    "results/leakage.csv",
    "results/main_cv.csv",
    "results/significance_cv.csv",
    "results/single_holdout.csv",
}
FORBIDDEN_COLUMNS = {
    "complaintid", "text", "text_clean", "timestamp", "latitude", "longitude",
    "lat", "lng", "y_true", "y_pred", "checkpoint_path",
}
WEIGHTS = (0.45, 0.30, 0.25)
TOLERANCE = 2e-4


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def rows(name: str) -> list[dict[str, str]]:
    path = RESULTS / name
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = {field.lower() for field in (reader.fieldnames or [])}
        unsafe = fields & FORBIDDEN_COLUMNS
        if unsafe:
            fail(f"{name} contains private columns: {sorted(unsafe)}")
        return list(reader)


def number(row: dict[str, str], key: str) -> float:
    try:
        return float(row[key])
    except (KeyError, ValueError) as exc:
        fail(f"invalid {key!r} in row {row}: {exc}")


def check_score(row: dict[str, str], suffix: str = "") -> None:
    expected = sum(weight * number(row, metric + suffix) for weight, metric in zip(
        WEIGHTS, ("category_macro_f1", "category_tail_f1", "opd_macro_f1")
    ))
    actual = number(row, "main_score" + suffix)
    if abs(expected - actual) > TOLERANCE:
        fail(f"main score mismatch for {row.get('model', '<unknown>')}: {actual} != {expected:.6f}")


def check_public_files() -> None:
    actual = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file() and not {".git", "__pycache__"} & set(path.relative_to(ROOT).parts)
    }
    unexpected = actual - ALLOWED
    missing = ALLOWED - actual
    if unexpected or missing:
        fail(f"file allowlist mismatch; unexpected={sorted(unexpected)}, missing={sorted(missing)}")
    if any(path.is_symlink() for path in ROOT.rglob("*") if ".git" not in path.parts):
        fail("symbolic links are not permitted")


def check_results() -> int:
    total = 0
    for name in ("single_holdout.csv", "main_cv.csv", "ablations.csv", "cross_source.csv"):
        current = rows(name)
        for row in current:
            suffix = "_mean" if name in {"main_cv.csv", "ablations.csv"} else ""
            check_score(row, suffix)
        total += len(current)

    leakage = rows("leakage.csv")
    for row in leakage:
        check_score(row, "_clean")
        check_score(row, "_leaky")
        for metric in ("category_macro_f1", "category_tail_f1", "opd_macro_f1", "main_score"):
            expected = number(row, metric + "_leaky") - number(row, metric + "_clean")
            if abs(expected - number(row, metric + "_delta")) > TOLERANCE:
                fail(f"{metric} delta mismatch for {row['model']}")
    total += len(leakage)

    significance = rows("significance_cv.csv")
    for row in significance:
        if int(row["n_pairs"]) != 15:
            fail(f"unexpected pair count for {row['metric']}: {row['n_pairs']}")
        p = number(row, "wilcoxon_p_holm")
        if not 0 <= p <= 1:
            fail(f"invalid Holm-adjusted p-value: {p}")
        if (p < 0.05) != (row["significant_0.05"].lower() == "true"):
            fail(f"significance flag mismatch for {row['metric']} vs {row['comparator']}")
    return total + len(significance)


def source_hashes() -> dict[str, str]:
    hashes = {}
    for line in (ROOT / "SOURCES.sha256").read_text(encoding="utf-8").splitlines():
        digest, name = line.split(maxsplit=1)
        hashes[name] = digest
    return hashes


def check_private_sources(private_root: Path) -> None:
    for name, expected in source_hashes().items():
        path = private_root / name
        if not path.is_file():
            fail(f"private source missing: {path}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            fail(f"private source changed: {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-root", type=Path, help="optional private repository root")
    args = parser.parse_args()
    check_public_files()
    count = check_results()
    if args.private_root:
        check_private_sources(args.private_root.resolve())
    print(f"PASS: {count} aggregate rows verified; no complaint-level files detected.")


if __name__ == "__main__":
    main()
