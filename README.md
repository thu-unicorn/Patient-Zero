# Patient-Zero

**Patient-Zero: Scaling Synthetic Patient Agents to Real-World Distributions without Real Patient Data**

**EMNLP 2026** · [Paper](https://aclanthology.org/2026.emnlp-main.1149/) · [PDF](https://aclanthology.org/2026.emnlp-main.1149.pdf) · [Dataset](#released-data) · [Citation](#citation)

Yunghwei Lai, Ziyue Wang, Weizhi Ma, and Yang Liu

Tsinghua University

Official repository for the paper published in the *Proceedings of the 2026
Conference on Empirical Methods in Natural Language Processing*.

## Overview

Patient-Zero builds synthetic patient records from medical knowledge and uses
those records to support interactive patient simulation. Its generation process
starts from medical knowledge and demographic priors, without using real patient
records as generation seeds.

The framework has two main components:

- **Medically-Aligned Hierarchical Synthesis** combines controlled attribute
  sampling, structured generation, deterministic checks, and semantic
  verification to construct patient profiles, symptoms, and examination results.
- **Dual-Track Cognitive Memory** combines persistent patient information with
  evolving interaction memory to support coherent responses during clinical
  conversations.

The paper evaluates record quality, patient-agent interaction, medical education,
and downstream medical reasoning. The study describes 60,000 records across six
clinical specialties and 98 disease types; see the [paper](https://aclanthology.org/2026.emnlp-main.1149/)
for the experimental setup and results.

The current repository release provides **4,064 synthetic patient records** and a
reproducible subset preparation script. These GPT-4.1 (`gpt-4.1-2025-04-14`)
records cover **98 distinct disease labels** across six specialties. The counts
below describe the files available in this repository.

## Released data

| Specialty | File | Available in selected source | Released | Source version |
| --- | --- | ---: | ---: | --- |
| Cardiology | [Cardiology.jsonl](data/Cardiology.jsonl) | 5,016 | 1,000 | v2 |
| Gastroenterology | [Gastroenterology.jsonl](data/Gastroenterology.jsonl) | 4,488 | 1,000 | v2 |
| General Surgery | [General_Surgery.jsonl](data/General_Surgery.jsonl) | 30 | 30 | v1-old |
| Neurology | [Neurology.jsonl](data/Neurology.jsonl) | 4,979 | 1,000 | v2 |
| Psychiatry | [Psychiatry.jsonl](data/Psychiatry.jsonl) | 34 | 34 | v1-old |
| Pulmonology | [Pulmonology.jsonl](data/Pulmonology.jsonl) | 4,999 | 1,000 | v2 |
| **Total** | | **19,546** | **4,064** | |

The target is 1,000 records per specialty. General Surgery and Psychiatry are
absent from the selected v2 source, so this release includes all 30 and 34 records
available in the v1 fallback. They remain **970 and 966 records short** of the
target. Records are sampled without replacement; none are duplicated to fill
these gaps.

Source directories, relative to the original project's `outputs/merge/`:

- Primary: `hierarchical-v2/gpt-4.1-2025-04-14/`
- Fallback: `hierarchical-v1/gpt-4.1-2025-04-14-old/`

## Format and loading

Each specialty file is UTF-8 JSON Lines, with one complete record per line.
All original fields and their values are preserved. Specialty is identified by
the filename; it is not added to the record.

| Fields | Content |
| --- | --- |
| `name`, `gender`, `age` | Synthetic patient identity and demographics |
| `disease`, `severity` | Disease label and severity |
| `symptom` | Symptoms and duration |
| `examination_results` | Examination names and generated findings |
| `medical_history`, `lifestyle_factor`, `vaccination_history`, `family_history` | History and background lists |
| `profile` | Structured demographic and disease-specific attributes |
| `record_id`, `generated_at` | Original generation identifier and timestamp |

Clone the repository and enter its directory:

```bash
git clone https://github.com/thu-unicorn/Patient-Zero.git
cd Patient-Zero
```

Load the patient records from the repository root using Python (standard library
only):

```python
import json
from pathlib import Path

data_dir = Path("data")
manifest = json.loads((data_dir / "manifest.json").read_text(encoding="utf-8"))
records_by_specialty = {}
for specialty, metadata in manifest["departments"].items():
    with (data_dir / metadata["file"]).open(encoding="utf-8") as handle:
        records_by_specialty[specialty] = [json.loads(line) for line in handle]

assert sum(map(len, records_by_specialty.values())) == 4064
```

These are generated research records. The source disease assignments and record
text are preserved; this release does not apply additional clinical filtering.

## Sampling and provenance

Primary data is used first. Fallback data is used only when a specialty is absent
or below the target. Within each source and specialty, records are stratified by
`disease` and `severity`. Proportional quotas are allocated with the largest
remainder method; ties are ordered by disease and severity.

Within each stratum, selection uses the ascending SHA-256 rank of
`seed + NUL + specialty + NUL + record_id`, with seed **42**. Output records retain
source line order, with primary records before fallback records. This selection
is deterministic. Original JSON text is retained with LF line endings.

- [manifest.json](data/manifest.json): source and release counts, shortages,
  per-stratum counts, source hashes, and output hashes.
- [provenance.jsonl](data/provenance.jsonl): source version, filename, line number,
  and `record_id` for each released record. This is metadata, not additional
  patient records.
- [SHA256SUMS](data/SHA256SUMS): checksums for the six specialty files and the two
  metadata files.

## Reproduction

The [preparation script](scripts/prepare_release.py) requires Python 3.9 or newer
and only the standard library. The full original source files are needed to
reproduce selection; they are not included in this subset.

From the repository root, replace `/path/to/Patient-zero` with the source project
location and use a new or empty output directory:

```bash
SOURCE_ROOT=/path/to/Patient-zero/outputs/merge
python scripts/prepare_release.py \
  --source-dir "$SOURCE_ROOT/hierarchical-v2/gpt-4.1-2025-04-14" \
  --source-label hierarchical-v2/gpt-4.1-2025-04-14 \
  --fallback-dir "$SOURCE_ROOT/hierarchical-v1/gpt-4.1-2025-04-14-old" \
  --fallback-label hierarchical-v1/gpt-4.1-2025-04-14-old \
  --output-dir reproduced_data \
  --per-department 1000 --seed 42 --allow-shortfall
```

`--allow-shortfall` explicitly permits the two documented shortages. Without it,
the script fails before writing any output when fewer than 1,000 records are
available. Existing nonempty output directories are never overwritten.

Verify the released files:

```bash
cd data
sha256sum -c SHA256SUMS
```

## License

See the repository's [MIT license](LICENSE).

## Citation

If you use Patient-Zero or these data in your research, please cite the paper.
The bibliographic details below follow the [ACL Anthology entry](https://aclanthology.org/2026.emnlp-main.1149/).

```bibtex
@inproceedings{lai-etal-2026-patient,
    title = "{Patient-Zero}: Scaling Synthetic Patient Agents to Real-World Distributions without Real Patient Data",
    author = "Lai, Yunghwei  and
      Wang, Ziyue  and
      Ma, Weizhi  and
      Liu, Yang",
    editor = "Lee, Hung-Yi  and
      Dev, Sunipa  and
      Li, Jessy  and
      Elliott, Desmond",
    booktitle = "Proceedings of the 2026 Conference on Empirical Methods in Natural Language Processing",
    month = oct,
    year = "2026",
    address = "Budapest, Hungary",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2026.emnlp-main.1149/",
    doi = "10.18653/2026.emnlp-main.1149",
    pages = "26339--26365",
    ISBN = "979-8-89176-459-0"
}
```

## Contact

For questions about the paper or dataset, please contact **Yunghwei Lai** at
[laiyunghwei@gmail.com](mailto:laiyunghwei@gmail.com).
