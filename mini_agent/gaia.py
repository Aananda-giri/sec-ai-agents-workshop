"""A tiny, offline GAIA-style evaluation harness.

Real GAIA (https://huggingface.co/datasets/gaia-benchmark/GAIA) is gated and
needs an HF token + accepted terms. SAMPLE_GAIA is a handful of questions in
the same spirit — general-knowledge, arithmetic, and lookup — so the eval
loop runs live with zero setup. load_hf_gaia() pulls the real thing if
you have datasets + HF_TOKEN configured.
"""

from __future__ import annotations

from typing import Callable

SAMPLE_GAIA = [
    {
        "question": "What is 17 * 23 - 45?",
        "answer": "346",
    },
    {
        "question": (
            "If a train travels 60 miles in 45 minutes, how many miles per "
            "hour is that?"
        ),
        "answer": "80",
    },
    {
        "question": "What year was the Eiffel Tower completed?",
        "answer": "1889",
    },
    {
        "question": (
            "Take the number of continents on Earth, multiply by the number "
            "of legs on a spider, then subtract 10. What's the result?"
        ),
        "answer": "46",
    },
]


def is_correct(prediction: str | None, answer: str) -> bool:
    """Case-insensitive exact match, ignoring surrounding whitespace."""
    if prediction is None:
        return False
    return prediction.strip().lower() == answer.strip().lower()


async def evaluate(
    make_agent: Callable[[], "Agent"],  # noqa: F821
    problems: list[dict] | None = None,
    verbose: bool = True,
) -> list[dict]:
    """Run a fresh agent (from make_agent()) on each problem and score it."""
    problems = problems if problems is not None else SAMPLE_GAIA
    results = []

    for problem in problems:
        agent = make_agent()
        prediction = await agent.run(problem["question"], verbose=False)
        correct = is_correct(prediction, problem["answer"])
        results.append({
            "question": problem["question"],
            "answer": problem["answer"],
            "prediction": prediction,
            "correct": correct,
        })
        if verbose:
            mark = "PASS" if correct else "FAIL"
            print(f"[{mark}] {problem['question']}")
            print(f"       expected={problem['answer']!r} got={prediction!r}\n")

    if verbose:
        n_correct = sum(r["correct"] for r in results)
        print(f"Score: {n_correct}/{len(results)}")

    return results


def load_hf_gaia(n: int = 5) -> list[dict]:
    """Load n real GAIA Level 1 questions. Requires `datasets` + a gated-access HF_TOKEN."""
    from datasets import load_dataset

    dataset = load_dataset("gaia-benchmark/GAIA", "2023_level1", split="validation")
    subset = dataset.select(range(min(n, len(dataset))))
    return [
        {"question": row["Question"], "answer": row["Final answer"]}
        for row in subset
    ]
