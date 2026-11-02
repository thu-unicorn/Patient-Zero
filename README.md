# Patient-Zero: Scaling Synthetic Patient Agents to Real-World Distributions without Real Patient Data

<p align="center">
  <a href="https://arxiv.org/abs/2509.11078">
    <img src="https://img.shields.io/badge/Publish-EMNLP%202026-4b44ce.svg" alt="EMNLP 2026">
  </a>
  <a href="https://arxiv.org/abs/2509.11078">
    <img src="https://img.shields.io/badge/Paper-arXiv-b31b1b.svg" alt="Paper on arXiv">
  </a>
  <a href="data/">
    <img src="https://img.shields.io/badge/Data-3%2C000%20records-blue.svg" alt="3,000 synthetic patient records">
  </a>
</p>

> 🎉 **Published at EMNLP 2026!** Explore our release of **3,000 synthetic patient records** across six clinical specialties. The paper is available on [arXiv](https://arxiv.org/abs/2509.11078).

**Patient-Zero** is a framework for creating synthetic patient records and interactive patient agents from medical knowledge. It combines structured record synthesis with a cognitive memory system to support diverse patient profiles and consistent clinical conversations, without using real patient records as generation seeds.

**Yunghwei Lai, Ziyue Wang, Weizhi Ma, and Yang Liu** · Tsinghua University

This is the official repository for the paper. The current release contains the patient-record subset in [`data/`](data/).

<p align="center">
  <img src="assets/method.png" alt="Patient-Zero hierarchical synthesis: disease outline standardization, epidemiological attribute permutation, symptom progression, and granular clinical expansion" width="100%">
</p>
<p align="center"><em>Medically-Aligned Hierarchical Synthesis with a global verify-and-regenerate mechanism.</em></p>

## 📰 News

- **[Nov 2026]** 🚀 **Dataset release:** 3,000 synthetic patient records are available as six JSONL files, covering 98 distinct disease labels.
- **[Oct 2026]** 🎉 **EMNLP 2026:** Patient-Zero is published in the *Proceedings of the 2026 Conference on Empirical Methods in Natural Language Processing*. Read the [paper](https://arxiv.org/abs/2509.11078).

## ✨ Key Features

- **Generation from Medical Knowledge:** Builds patient records from medical knowledge and demographic priors, enabling controlled variation in patient characteristics.
- **Medically-Aligned Hierarchical Synthesis:** Combines attribute sampling, structured generation, deterministic clinical checks, and semantic verification to construct profiles, symptoms, and examination findings.
- **Dual-Track Cognitive Memory:** Maintains persistent patient information alongside evolving interaction memory to support factual consistency and persona adherence during clinical inquiries.
- **Evaluation across Multiple Settings:** The paper studies record quality, patient-agent interaction, physician assessments, medical education, and downstream medical reasoning.

## 📦 Dataset

The paper describes a corpus of **60,000 records across six specialties and 98 disease types**. This repository provides a **3,000-record subset** generated with GPT-4.1 (`gpt-4.1-2025-04-14`).

| Specialty | Records | Download |
| :--- | ---: | :--- |
| Cardiology | 500 | [Cardiology.jsonl](data/Cardiology.jsonl) |
| Gastroenterology | 500 | [Gastroenterology.jsonl](data/Gastroenterology.jsonl) |
| General Surgery | 500 | [General_Surgery.jsonl](data/General_Surgery.jsonl) |
| Neurology | 500 | [Neurology.jsonl](data/Neurology.jsonl) |
| Psychiatry | 500 | [Psychiatry.jsonl](data/Psychiatry.jsonl) |
| Pulmonology | 500 | [Pulmonology.jsonl](data/Pulmonology.jsonl) |
| **Total** | **3,000** | |

The release contains **500 records per specialty**, for **3,000 records in total**.

## 🏆 Main Results

The following results are reported in the [paper](https://arxiv.org/abs/2509.11078) and refer to its full experimental setup. The downloadable subset above contains 3,000 records.

<p align="center">
  <img src="assets/data_distribution.png" alt="Epidemiological manifold coverage and prevalence alignment across demographic, socioeconomic, and lifestyle attributes" width="100%">
</p>
<p align="center"><em>Distribution analysis from the paper: epidemiological coverage and attribute-level prevalence alignment.</em></p>

**Downstream medical reasoning (Table 3).** Training with Patient-Zero data improves Qwen3-8B on both evaluated benchmarks.

| Model | MedQA (%) | MMLU (%) |
| :--- | :---: | :---: |
| Qwen3-8B (Base) | 61.00 | 69.50 |
| Qwen3-8B + Patient-Zero | **85.00** | **83.00** |

**Patient-agent interaction (Table 2).** The memory system supports consistency and resistance to misleading suggestions during multi-turn clinical inquiries.

| Metric | Without Dual-Track Cognitive Memory | Patient-Zero |
| :--- | :---: | :---: |
| Logical consistency ↑ | 81.36 | **100.00** |
| Factual recall ↑ | 7.88 | **33.27** |
| Persona alignment ↑ | 61.10 | **83.70** |
| Stylistic stability ↑ | 46.61 | **75.50** |
| Hallucination rate ↓ | 10.45 | **1.82** |
| Inducibility resistance ↑ | 69.17 | **97.22** |

## 👥 Human Evaluation

In the paper's blinded physician evaluation, Patient-Zero receives mean ratings of **3.85/5 for diversity**, **3.90/5 for consistency**, and **4.00/5 for completeness** (Table 14).

<p align="center">
  <img src="assets/turing_test.png" alt="Physician evaluation of human-versus-AI record discrimination and ratings for linguistic quality, diversity, consistency, and completeness" width="680">
</p>
<p align="center"><em>Human evaluation: record-source discrimination and expert ratings of data quality.</em></p>

A separate study with **16 medical students** reports positive perceptions of educational usefulness, including **6.31/7** for providing a low-risk practice environment and **6.06/7** for teaching-tool utility. These ratings measure perceived usability and educational value.

## 🔬 Ablation Studies

- **Hierarchical Synthesis:** Removing controlled sampling, deterministic checks, or semantic verification reduces record quality. The full synthesis configuration reaches **95.86 consistency** and **99.55 completeness** in the stage-wise ablation study (Table 4).
- **Cognitive Memory:** Removing Dual-Track Cognitive Memory reduces logical consistency from **100.00 to 81.36** and increases hallucination rate from **1.82 to 10.45** in the interaction evaluation (Table 2).

## 📜 Citation

Please cite our paper when using Patient-Zero or its data in your research. Citation metadata follows the [arXiv entry](https://arxiv.org/abs/2509.11078).

```bibtex
@misc{lai2025patientzero,
    title = {{Patient-Zero}: Scaling Synthetic Patient Agents to Real-World Distributions without Real Patient Data},
    author = {Yunghwei Lai and Ziyue Wang and Weizhi Ma and Yang Liu},
    year = {2025},
    eprint = {2509.11078},
    archivePrefix = {arXiv},
    primaryClass = {cs.AI},
    url = {https://arxiv.org/abs/2509.11078},
    doi = {10.48550/arXiv.2509.11078}
}
```

## 💬 Contact & Questions

For questions or collaborations, please contact **Yunghwei Lai** at [**laiyunghwei@gmail.com**](mailto:laiyunghwei@gmail.com). You can also [open an issue](https://github.com/thu-unicorn/Patient-Zero/issues) to discuss the paper or dataset.
