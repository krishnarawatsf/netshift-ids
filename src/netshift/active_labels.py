"""Label-budget selection strategies that never inspect target labels."""

import numpy as np


def budget_count(pool_size: int, budget: float) -> int:
    if pool_size < 0:
        raise ValueError("pool_size cannot be negative")
    if not 0 <= budget <= 1:
        raise ValueError("budget must be between 0 and 1")
    if pool_size == 0 or budget == 0:
        return 0
    return min(pool_size, max(1, int(round(pool_size * budget))))


def random_selection(pool_size: int, budget: float, seed: int) -> np.ndarray:
    """Choose a reproducible uniform subset without reading target labels."""
    count = budget_count(pool_size, budget)
    if count == 0:
        return np.empty(0, dtype=np.int64)
    return np.sort(np.random.default_rng(seed).choice(pool_size, size=count, replace=False))


def uncertainty_selection(probabilities: np.ndarray, budget: float) -> np.ndarray:
    """Choose the least-confident examples, with stable index-based tie breaking."""
    probabilities = np.asarray(probabilities, dtype=np.float64)
    if probabilities.ndim != 2 or probabilities.shape[1] < 2:
        raise ValueError("probabilities must have shape (n_samples, n_classes>=2)")
    if not np.isfinite(probabilities).all():
        raise ValueError("probabilities must be finite")
    if (probabilities < 0).any() or (probabilities > 1).any():
        raise ValueError("probabilities must be between 0 and 1")
    if not np.allclose(probabilities.sum(axis=1), 1.0, atol=1e-5):
        raise ValueError("each probability row must sum to 1")

    count = budget_count(len(probabilities), budget)
    if count == 0:
        return np.empty(0, dtype=np.int64)
    confidence = probabilities.max(axis=1)
    return np.sort(np.lexsort((np.arange(len(probabilities)), confidence))[:count])
