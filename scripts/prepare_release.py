#!/usr/bin/env python3
"""Prepare a reproducible, stratified subset of Patient-Zero JSONL records."""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path


DEPARTMENTS = (
    "Cardiology", "Gastroenterology", "General_Surgery",
    "Neurology", "Psychiatry", "Pulmonology",
)
REQUIRED_FIELDS = {
    "name", "gender", "age", "disease", "severity", "symptom",
    "examination_results", "medical_history", "lifestyle_factor",
    "vaccination_history", "family_history", "profile", "record_id", "generated_at",
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def encode_json(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def select_records(rows, count, seed, department):
    """Use proportional disease/severity quotas and deterministic hash ranking."""
    groups = defaultdict(list)
    for row in rows:
        groups[(row["data"]["disease"], row["data"]["severity"])].append(row)
    total = len(rows)
    quotas = {key: count * len(group) // total for key, group in groups.items()}
    remainder_order = sorted(
        groups, key=lambda key: (-(count * len(groups[key]) % total), key)
    )
    for key in remainder_order[:count - sum(quotas.values())]:
        quotas[key] += 1
    selected = []
    for key in sorted(groups):
        ranked = sorted(groups[key], key=lambda row: (
            sha256(f"{seed}\0{department}\0{row['data']['record_id']}".encode("utf-8")),
            row["data"]["record_id"],
        ))
        selected.extend(ranked[:quotas[key]])
    selected.sort(key=lambda row: row["line"])
    strata = [
        {"disease": key[0], "severity": key[1], "source_count": len(groups[key]),
         "released_count": quotas[key]}
        for key in sorted(groups)
    ]
    return selected, strata


def prepare(args):
    if args.per_department <= 0:
        raise ValueError("--per-department must be positive")
    if len(set(args.departments)) != len(args.departments):
        raise ValueError("Repeated department names are not allowed")
    if bool(args.fallback_dir) != bool(args.fallback_label):
        raise ValueError("--fallback-dir and --fallback-label must be provided together")
    sources = [(args.source_dir, args.source_label)]
    if args.fallback_dir:
        if args.fallback_label == args.source_label:
            raise ValueError("Primary and fallback source labels must differ")
        sources.append((args.fallback_dir, args.fallback_label))
    output = args.output_dir
    if output.exists() and any(output.iterdir()):
        raise ValueError(f"Output directory must be empty: {output}")
    files = {}
    provenance = []
    summaries = {}
    all_ids = set()
    for department in args.departments:
        selected = []
        available = []
        source_summaries = []
        department_ids = set()
        for source_dir, label in sources:
            if len(selected) == args.per_department:
                break
            source = source_dir / f"{department}.jsonl"
            # Historical GPT-4.1 v1 exports use this misspelling in the filename.
            if department == "Gastroenterology" and not source.exists():
                alias = source_dir / "Gastroentology.jsonl"
                if alias.exists():
                    source = alias
            if not source.exists():
                source_summaries.append({
                    "source_label": label, "source_file": source.name,
                    "status": "missing", "source_records": 0, "released_records": 0,
                })
                continue
            raw = source.read_bytes()
            rows = []
            source_ids = set()
            for line_number, line in enumerate(raw.split(b"\n"), 1):
                if not line.strip():
                    continue
                line = line.removesuffix(b"\r")
                row = json.loads(line)
                if not isinstance(row, dict) or not REQUIRED_FIELDS.issubset(row):
                    raise ValueError(f"Missing record fields: {source}:{line_number}")
                for key in ("record_id", "disease", "severity"):
                    if not isinstance(row[key], str) or not row[key].strip():
                        raise ValueError(f"Invalid {key}: {source}:{line_number}")
                record_id = row["record_id"]
                if record_id in source_ids:
                    raise ValueError(f"Duplicate record_id within source: {source}:{line_number}")
                source_ids.add(record_id)
                if record_id in department_ids:
                    continue  # Prefer the primary source when fallback overlaps.
                if record_id in all_ids:
                    raise ValueError(f"record_id shared across departments: {source}:{line_number}")
                department_ids.add(record_id)
                rows.append({
                    "line": line_number, "data": row, "raw": line,
                    "source_label": label, "source_file": source.name,
                })
            count = min(args.per_department - len(selected), len(rows))
            chosen, strata = select_records(rows, count, args.seed, department) if rows else ([], [])
            selected.extend(chosen)
            available.extend(rows)
            source_summaries.append({
                "source_label": label, "source_file": source.name, "status": "read",
                "source_sha256": sha256(raw), "source_records": len(source_ids),
                "eligible_records": len(rows), "duplicates_skipped": len(source_ids) - len(rows),
                "released_records": count, "strata": strata,
            })
        all_ids.update(department_ids)
        count = len(selected)
        if count < args.per_department and not args.allow_shortfall:
            raise ValueError(
                f"{department}: {count} records available, "
                f"{args.per_department} requested; no files written"
            )
        if not count:
            raise ValueError(f"No records found for {department}")
        filename = f"{department}.jsonl"
        content = b"".join(row["raw"] + b"\n" for row in selected)
        files[filename] = content
        for release_line, row in enumerate(selected, 1):
            provenance.append({
                "file": filename, "release_line": release_line,
                "source_label": row["source_label"],
                "source_file": row["source_file"], "source_line": row["line"],
                "record_id": row["data"]["record_id"],
            })
        summaries[department] = {
            "sources": source_summaries, "source_records": len(available),
            "released_records": count,
            "shortfall": args.per_department - count,
            "source_diseases": len({row["data"]["disease"] for row in available}),
            "released_diseases": len({row["data"]["disease"] for row in selected}),
            "released_severity_counts": dict(sorted(Counter(
                row["data"]["severity"] for row in selected
            ).items())),
            "file": filename, "bytes": len(content), "sha256": sha256(content),
        }
    manifest = {
        "source_priority": [label for _, label in sources],
        "source_policy": "Use primary records first; fill remaining quota from fallback without replacement",
        "requested_per_department": args.per_department,
        "total_released_records": sum(s["released_records"] for s in summaries.values()),
        "sampling": {
            "seed": args.seed, "stratification": ["disease", "severity"],
            "quota_allocation": "Proportional largest remainder; ties sorted by disease/severity",
            "within_stratum": "Ascending SHA-256 of seed + NUL + department + NUL + record_id",
            "output_order": "Source priority, then original source line order",
            "replacement": False,
        },
        "record_transformations": "None; source JSON text is retained with LF line endings",
        "departments": summaries,
    }
    files["manifest.json"] = encode_json(manifest)
    files["provenance.jsonl"] = b"".join(
        (json.dumps(row, ensure_ascii=False) + "\n").encode("utf-8") for row in provenance
    )
    files["SHA256SUMS"] = "".join(
        f"{sha256(content)}  {name}\n" for name, content in sorted(files.items())
    ).encode("utf-8")
    # All inputs are validated before any output is written.
    output.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        (output / name).write_bytes(content)
    for department, summary in summaries.items():
        print(f"{department}: {summary['released_records']}/{summary['source_records']} records")
    print(f"Total: {manifest['total_released_records']} records")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--source-label", required=True, help="Public provenance label; avoid local paths")
    parser.add_argument("--fallback-dir", type=Path, help="Supplement insufficient primary data")
    parser.add_argument("--fallback-label", help="Public provenance label for fallback data")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--departments", choices=DEPARTMENTS, nargs="+", default=list(DEPARTMENTS))
    parser.add_argument("--per-department", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--allow-shortfall", action="store_true", help="Explicitly permit fewer records")
    args = parser.parse_args()
    try:
        prepare(args)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
