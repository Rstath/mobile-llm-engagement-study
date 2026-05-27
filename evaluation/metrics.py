from typing import List, Dict, Any

import numpy as np

from evaluation.embeddings import embed_texts, cosine


def clamp01(value: float) -> float:
    if np.isnan(value) or np.isinf(value):
        return 0.0
    return float(max(0.0, min(1.0, value)))


def compute_metrics(transcript: List[Dict[str, Any]], topic_prompt: str, embedder) -> Dict[str, float]:
    texts = [turn.get("text", "").strip() for turn in transcript if turn.get("text", "").strip()]
    speakers = [turn.get("speaker", "") for turn in transcript if turn.get("text", "").strip()]

    if len(texts) < 2:
        return {
            "coherence": 0.0,
            "topic_consistency": 0.0,
            "novelty": 0.0,
            "question_rate": 0.0,
            "turn_balance": 0.0,
            "engagement_score": 0.0,
        }

    utterance_embeddings = embed_texts(texts, embedder)
    topic_embedding = embed_texts([topic_prompt], embedder)[0]

    pair_sims = [
        clamp01(cosine(utterance_embeddings[i - 1], utterance_embeddings[i]))
        for i in range(1, len(utterance_embeddings))
    ]
    topic_sims = [
        clamp01(cosine(topic_embedding, utterance_embedding))
        for utterance_embedding in utterance_embeddings
    ]

    coherence = clamp01(float(np.mean(pair_sims)))
    topic_consistency = clamp01(float(np.mean(topic_sims)))
    novelty = clamp01(float(np.mean([1.0 - similarity for similarity in pair_sims])))
    question_rate = clamp01(float(np.mean([1 if "?" in text else 0 for text in texts])))

    n_human = sum(1 for speaker in speakers if speaker == "Human")
    n_agent = sum(1 for speaker in speakers if speaker == "Agent")
    turn_balance = clamp01(1 - abs(n_human - n_agent) / max((n_human + n_agent), 1))

    engagement_score = clamp01(
        0.30 * coherence
        + 0.25 * topic_consistency
        + 0.20 * novelty
        + 0.15 * question_rate
        + 0.10 * turn_balance
    )

    return {
        "coherence": coherence,
        "topic_consistency": topic_consistency,
        "novelty": novelty,
        "question_rate": question_rate,
        "turn_balance": turn_balance,
        "engagement_score": engagement_score,
    }
