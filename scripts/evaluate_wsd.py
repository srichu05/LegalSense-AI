"""WSD Evaluation Script for LegalSense.

Evaluates LegalSense's Extended Lesk WSD engine against the standard Most Frequent Sense
(First Sense) WordNet baseline on the manually annotated legal-context evaluation dataset
(data/evaluation/wsd_eval_set.json).

Computes:
- Overall Accuracy
- Macro-F1 across sense labels
- Coverage (non-abstained predictions)
- Abstention rate
- Selective Accuracy (accuracy on high-confidence, non-uncertain predictions)
- Domain-specific breakdown (legal vs. general)
- Per-term accuracy and failure analysis
"""

from __future__ import annotations

import json
import logging
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

# Ensure src/ is on sys.path
src_dir = str(Path(__file__).resolve().parent.parent / "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from nltk.corpus import wordnet as wn
from sklearn.metrics import f1_score

from legalsense.legal_glossary import lookup_term
from legalsense.lesk_wsd import disambiguate

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def load_evaluation_dataset(dataset_path: Path) -> list[dict[str, Any]]:
    with open(dataset_path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_wsd(dataset: list[dict[str, Any]]) -> dict[str, Any]:
    total_examples = len(dataset)
    valid_wn_examples = [ex for ex in dataset if ex["gold_synset_id"] != "NONE_NOT_IN_WORDNET"]
    non_wn_examples = [ex for ex in dataset if ex["gold_synset_id"] == "NONE_NOT_IN_WORDNET"]

    gold_labels = []
    baseline_preds = []
    lesk_preds = []
    lesk_uncertain_flags = []

    domain_counts = defaultdict(lambda: {"total": 0, "baseline_correct": 0, "lesk_correct": 0})
    term_counts = defaultdict(lambda: {"total": 0, "baseline_correct": 0, "lesk_correct": 0})

    for ex in valid_wn_examples:
        target = ex["target_term"]
        sentence = ex["context_sentence"]
        gold_id = ex["gold_synset_id"]
        domain = ex["domain"]

        gold_labels.append(gold_id)

        # Baseline: Most Frequent Sense / First Available Sense in WordNet
        candidate_synsets = wn.synsets(target, pos=wn.NOUN)
        mfs_pred = candidate_synsets[0].name() if candidate_synsets else None
        baseline_preds.append(mfs_pred)

        # LegalSense Extended Lesk WSD
        legal_entry = lookup_term(target)
        result = disambiguate(sentence, target, legal_entry=legal_entry)

        pred_id = result.selected_sense.synset_id if result.selected_sense else None
        lesk_preds.append(pred_id)
        lesk_uncertain_flags.append(result.uncertain)

        # Accuracy tracking
        is_baseline_correct = (mfs_pred == gold_id)
        is_lesk_correct = (pred_id == gold_id)

        domain_counts[domain]["total"] += 1
        if is_baseline_correct:
            domain_counts[domain]["baseline_correct"] += 1
        if is_lesk_correct:
            domain_counts[domain]["lesk_correct"] += 1

        term_counts[target]["total"] += 1
        if is_baseline_correct:
            term_counts[target]["baseline_correct"] += 1
        if is_lesk_correct:
            term_counts[target]["lesk_correct"] += 1

    # Metrics computation
    n = len(valid_wn_examples)
    baseline_correct = sum(1 for p, g in zip(baseline_preds, gold_labels) if p == g)
    lesk_correct = sum(1 for p, g in zip(lesk_preds, gold_labels) if p == g)

    baseline_acc = baseline_correct / n if n > 0 else 0.0
    lesk_acc = lesk_correct / n if n > 0 else 0.0

    # Coverage and abstention
    non_abstained = sum(1 for p in lesk_preds if p is not None)
    coverage = non_abstained / n if n > 0 else 0.0
    abstention_rate = 1.0 - coverage

    # Selective accuracy (where not uncertain)
    certain_indices = [i for i, unc in enumerate(lesk_uncertain_flags) if not unc]
    if certain_indices:
        certain_correct = sum(1 for i in certain_indices if lesk_preds[i] == gold_labels[i])
        selective_acc = certain_correct / len(certain_indices)
    else:
        selective_acc = lesk_acc

    # Macro-F1 across sense IDs
    all_classes = sorted(list(set(gold_labels) | set(p for p in baseline_preds if p) | set(p for p in lesk_preds if p)))
    baseline_f1 = f1_score(gold_labels, [p or "ABSTAIN" for p in baseline_preds], labels=all_classes, average="macro", zero_division=0)
    lesk_f1 = f1_score(gold_labels, [p or "ABSTAIN" for p in lesk_preds], labels=all_classes, average="macro", zero_division=0)

    return {
        "total_examples": total_examples,
        "valid_wn_examples": n,
        "non_wn_examples": len(non_wn_examples),
        "baseline": {
            "name": "Most Frequent Sense (MFS / First Sense)",
            "correct": baseline_correct,
            "accuracy": round(baseline_acc, 4),
            "macro_f1": round(baseline_f1, 4),
        },
        "extended_lesk": {
            "name": "LegalSense Extended Lesk WSD",
            "correct": lesk_correct,
            "accuracy": round(lesk_acc, 4),
            "macro_f1": round(lesk_f1, 4),
            "coverage": round(coverage, 4),
            "abstention_rate": round(abstention_rate, 4),
            "selective_accuracy": round(selective_acc, 4),
            "certain_count": len(certain_indices),
        },
        "domain_breakdown": {
            k: {
                "total": v["total"],
                "baseline_accuracy": round(v["baseline_correct"] / v["total"], 4) if v["total"] > 0 else 0.0,
                "lesk_accuracy": round(v["lesk_correct"] / v["total"], 4) if v["total"] > 0 else 0.0,
            }
            for k, v in domain_counts.items()
        },
        "term_breakdown": {
            k: {
                "total": v["total"],
                "baseline_accuracy": round(v["baseline_correct"] / v["total"], 4) if v["total"] > 0 else 0.0,
                "lesk_accuracy": round(v["lesk_correct"] / v["total"], 4) if v["total"] > 0 else 0.0,
            }
            for k, v in term_counts.items()
        },
        "out_of_wordnet_cases": [
            {
                "id": ex["id"],
                "term": ex["target_term"],
                "sentence": ex["context_sentence"],
                "intended_sense": ex["intended_sense_label"],
                "legal_glossary_matched": lookup_term(ex["target_term"]) is not None,
            }
            for ex in non_wn_examples
        ],
    }


def main():
    root = Path(__file__).resolve().parent.parent
    dataset_path = root / "data" / "evaluation" / "wsd_eval_set.json"
    if not dataset_path.exists():
        logger.error(f"Dataset not found at {dataset_path}")
        return

    dataset = load_evaluation_dataset(dataset_path)
    logger.info(f"Loaded {len(dataset)} evaluation instances from {dataset_path.name}")

    results = evaluate_wsd(dataset)
    print("\n" + "=" * 65)
    print(" LEGALSENSE — WORD SENSE DISAMBIGUATION EVALUATION REPORT")
    print("=" * 65)
    print(f"Total Evaluated Instances: {results['total_examples']}")
    print(f"WordNet-Valid Instances:  {results['valid_wn_examples']}")
    print(f"Out-of-WordNet Instances: {results['non_wn_examples']} (handled via Curated Legal Glossary)")
    print("-" * 65)
    b = results["baseline"]
    print(f"BASELINE: {b['name']}")
    print(f"  Accuracy:  {b['accuracy'] * 100:.2f}% ({b['correct']}/{results['valid_wn_examples']})")
    print(f"  Macro-F1:  {b['macro_f1']:.4f}")
    print("-" * 65)
    l = results["extended_lesk"]
    print(f"PROPOSED: {l['name']}")
    print(f"  Accuracy:           {l['accuracy'] * 100:.2f}% ({l['correct']}/{results['valid_wn_examples']})")
    print(f"  Macro-F1:           {l['macro_f1']:.4f}")
    print(f"  Coverage:           {l['coverage'] * 100:.2f}%")
    print(f"  Abstention Rate:    {l['abstention_rate'] * 100:.2f}%")
    print(f"  Selective Accuracy: {l['selective_accuracy'] * 100:.2f}% (on {l['certain_count']} confident cases)")
    print("-" * 65)
    print("ACCURACY BY DOMAIN CONTEXT:")
    for dom, stats in results["domain_breakdown"].items():
        print(f"  [{dom.upper()}] ({stats['total']} instances): Baseline = {stats['baseline_accuracy']*100:.1f}% | Extended Lesk = {stats['lesk_accuracy']*100:.1f}%")
    print("-" * 65)
    print("ACCURACY BY TARGET TERM:")
    for term, stats in sorted(results["term_breakdown"].items()):
        print(f"  {term:15s} (n={stats['total']}): Baseline = {stats['baseline_accuracy']*100:.1f}% | Extended Lesk = {stats['lesk_accuracy']*100:.1f}%")
    print("=" * 65 + "\n")

    # Save results as JSON artifact
    results_path = root / "data" / "evaluation" / "wsd_eval_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Saved evaluation metrics to {results_path}")


if __name__ == "__main__":
    main()
