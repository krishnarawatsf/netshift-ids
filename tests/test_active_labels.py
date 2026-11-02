import numpy as np
import pytest

from netshift.active_labels import budget_count, random_selection, uncertainty_selection


def test_budget_count_rounds_and_caps():
    assert budget_count(100, 0) == 0
    assert budget_count(100, 0.01) == 1
    assert budget_count(100, 0.05) == 5
    assert budget_count(3, 0.10) == 1
    assert budget_count(3, 1) == 3


def test_random_selection_is_reproducible_without_replacement():
    first = random_selection(100, 0.1, seed=42)
    second = random_selection(100, 0.1, seed=42)
    assert len(first) == len(second) == 10
    assert np.array_equal(first, second)
    assert len(np.unique(first)) == 10


def test_uncertainty_selects_lowest_confidence_with_stable_ties():
    probabilities = np.array([
        [0.99, 0.01],
        [0.55, 0.45],
        [0.50, 0.50],
        [0.50, 0.50],
    ])
    assert uncertainty_selection(probabilities, 0.5).tolist() == [2, 3]


@pytest.mark.parametrize("probabilities", [
    np.array([[0.7, 0.7]]),
    np.array([[float("nan"), 1.0]]),
    np.array([[-0.1, 1.1]]),
    np.array([[0.7]]),
])
def test_uncertainty_rejects_invalid_probabilities(probabilities):
    with pytest.raises(ValueError):
        uncertainty_selection(probabilities, 0.5)


def test_budget_validation():
    with pytest.raises(ValueError):
        budget_count(10, -0.1)
    with pytest.raises(ValueError):
        budget_count(10, 1.1)
    with pytest.raises(ValueError):
        budget_count(-1, 0.1)
