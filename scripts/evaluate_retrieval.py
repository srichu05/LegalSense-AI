"""Retrieval Evaluation Script for LegalSense.

Evaluates the compound TF-IDF + Lexical + Legal Glossary passage retriever
against a pure TF-IDF baseline on the manually annotated retrieval query dataset
(data/evaluation/retrieval_eval_set.json) using the bundled sample legal corpus.

Computes:
- Mean Reciprocal Rank (MRR)
- Precision@1 and Precision@3
- Recall@1 and Recall@3
- Negative / Out-of-domain query discrimination
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

# Ensure src/ is on sys.path
src_dir = str(Path(__file__).resolve().parent.parent / "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from legalsense.document_ingestion import ingest_document
from legalsense.retrieval import PassageRetriever
from legalsense.segmentation import segment_document

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def load_bundled_corpus(sample_dir: Path) -> list:
    passages = []
    for file_path in sorted(sample_dir.glob("*.txt")):
        doc = ingest_document(file_path)
        passages.extend(segment_document(doc))
    return passages


def load_query_dataset(dataset_path: Path) -> list[dict[str, Any]]:
    with open(dataset_path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_engine(retriever: PassageRetriever, queries: list[dict[str, Any]], all_passages: list) -> dict[str, Any]:
    rr_list = []
    p1_list = []
    p3_list = []
    r1_list = []
    r3_list = []

    positive_queries_count = 0
    negative_queries_count = 0

    detailed_results = []

    for item in queries:
        qid = item["query_id"]
        qtext = item["query"]
        relevant_specs = item.get("relevant_passages", [])

        # Find target passage indices in all_passages
        relevant_indices = set()
        for spec in relevant_specs:
            doc_name = spec["document_name"]
            p_idx = spec["passage_index"]
            # Locate corresponding passage in all_passages list
            doc_passages = [i for i, p in enumerate(all_passages) if p.document_name == doc_name]
            if p_idx < len(doc_passages):
                relevant_indices.add(doc_passages[p_idx])

        hits = retriever.search(qtext, top_k=3)

        # Match hits back to all_passages indices
        hit_indices = []
        for h in hits:
            for idx, p in enumerate(all_passages):
                if p.document_name == h.document_name and p.text == h.passage:
                    hit_indices.append(idx)
                    break

        if not relevant_specs:
            # Negative query
            negative_queries_count += 1
            max_score = hits[0].score if hits else 0.0
            detailed_results.append({
                "query_id": qid,
                "query": qtext,
                "type": "negative",
                "max_score": round(max_score, 4),
                "safe": max_score < 0.2,
            })
            continue

        positive_queries_count += 1
        num_relevant = len(relevant_indices)

        # Reciprocal Rank (RR)
        rr = 0.0
        for rank, h_idx in enumerate(hit_indices, start=1):
            if h_idx in relevant_indices:
                rr = 1.0 / rank
                break
        rr_list.append(rr)

        # Precision@1 & Recall@1
        top1_hit = hit_indices[0] if hit_indices else -1
        is_top1_relevant = top1_hit in relevant_indices
        p1 = 1.0 if is_top1_relevant else 0.0
        r1 = 1.0 / num_relevant if is_top1_relevant else 0.0
        p1_list.append(p1)
        r1_list.append(r1)

        # Precision@3 & Recall@3
        hits_at_3 = set(hit_indices[:3])
        correct_at_3 = len(hits_at_3 & relevant_indices)
        p3 = correct_at_3 / min(3, len(hit_indices)) if hit_indices else 0.0
        r3 = correct_at_3 / num_relevant if num_relevant > 0 else 0.0
        p3_list.append(p3)
        r3_list.append(r3)

        detailed_results.append({
            "query_id": qid,
            "query": qtext,
            "type": "positive",
            "reciprocal_rank": round(rr, 4),
            "p@1": round(p1, 4),
            "r@1": round(r1, 4),
            "p@3": round(p3, 4),
            "r@3": round(r3, 4),
            "top_hit_score": round(hits[0].score, 4) if hits else 0.0,
            "top_hit_document": hits[0].document_name if hits else None,
        })

    mrr = sum(rr_list) / len(rr_list) if rr_list else 0.0
    mean_p1 = sum(p1_list) / len(p1_list) if p1_list else 0.0
    mean_p3 = sum(p3_list) / len(p3_list) if p3_list else 0.0
    mean_r1 = sum(r1_list) / len(r1_list) if r1_list else 0.0
    mean_r3 = sum(r3_list) / len(r3_list) if r3_list else 0.0

    return {
        "positive_queries": positive_queries_count,
        "negative_queries": negative_queries_count,
        "mrr": round(mrr, 4),
        "precision@1": round(mean_p1, 4),
        "precision@3": round(mean_p3, 4),
        "recall@1": round(mean_r1, 4),
        "recall@3": round(mean_r3, 4),
        "detailed_results": detailed_results,
    }


def main():
    root = Path(__file__).resolve().parent.parent
    sample_dir = root / "data" / "sample_documents"
    query_path = root / "data" / "evaluation" / "retrieval_eval_set.json"

    passages = load_bundled_corpus(sample_dir)
    queries = load_query_dataset(query_path)

    logger.info(f"Loaded {len(passages)} passages from bundled sample documents.")
    logger.info(f"Loaded {len(queries)} retrieval evaluation queries.")

    # 1. Baseline: Pure TF-IDF (1.0 TF-IDF, 0.0 Lexical, 0.0 WSD Boost)
    baseline_retriever = PassageRetriever(passages, tfidf_weight=1.0, lexical_weight=0.0, wsd_boost_weight=0.0)
    baseline_metrics = evaluate_engine(baseline_retriever, queries, passages)

    # 2. Proposed: Compound LegalSense Engine (0.6 TF-IDF, 0.3 Lexical, 0.1 WSD Boost)
    compound_retriever = PassageRetriever(passages, tfidf_weight=0.6, lexical_weight=0.3, wsd_boost_weight=0.1)
    compound_metrics = evaluate_engine(compound_retriever, queries, passages)

    print("\n" + "=" * 65)
    print(" LEGALSENSE — PASSAGE RETRIEVAL EVALUATION REPORT")
    print("=" * 65)
    print(f"Corpus Size: {len(passages)} passages across {len(list(sample_dir.glob('*.txt')))} documents")
    print(f"Evaluated Queries: {len(queries)} ({compound_metrics['positive_queries']} positive, {compound_metrics['negative_queries']} out-of-domain)")
    print("-" * 65)
    print("METRIC COMPARISON:")
    print(f"  Mean Reciprocal Rank (MRR):")
    print(f"    • Baseline (Pure TF-IDF):          {baseline_metrics['mrr']:.4f}")
    print(f"    • LegalSense (Compound WSD+TFIDF):  {compound_metrics['mrr']:.4f}")
    print(f"  Precision@1:")
    print(f"    • Baseline (Pure TF-IDF):          {baseline_metrics['precision@1'] * 100:.1f}%")
    print(f"    • LegalSense (Compound WSD+TFIDF):  {compound_metrics['precision@1'] * 100:.1f}%")
    print(f"  Recall@1:")
    print(f"    • Baseline (Pure TF-IDF):          {baseline_metrics['recall@1'] * 100:.1f}%")
    print(f"    • LegalSense (Compound WSD+TFIDF):  {compound_metrics['recall@1'] * 100:.1f}%")
    print(f"  Precision@3:")
    print(f"    • Baseline (Pure TF-IDF):          {baseline_metrics['precision@3'] * 100:.1f}%")
    print(f"    • LegalSense (Compound WSD+TFIDF):  {compound_metrics['precision@3'] * 100:.1f}%")
    print("-" * 65)
    print("NEGATIVE QUERY HANDLING:")
    neg = [d for d in compound_metrics["detailed_results"] if d["type"] == "negative"][0]
    print(f"  Query: \"{neg['query']}\"")
    print(f"  Top Score: {neg['max_score']} (Safely suppressed: {neg['safe']})")
    print("=" * 65 + "\n")

    # Save results
    results_path = root / "data" / "evaluation" / "retrieval_eval_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump({
            "baseline_pure_tfidf": baseline_metrics,
            "legalsense_compound": compound_metrics,
        }, f, indent=2)
    logger.info(f"Saved retrieval metrics to {results_path}")


if __name__ == "__main__":
    main()
