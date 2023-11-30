# Standard library imports
from typing import Any

# Related third-party imports
import numpy as np
import pytest

# Local application/library specific imports
from spectrostaff.data import DataCollector


def test_data_collector_initialization():
    """
    Test that a DataCollector object is correctly initialized.
    """
    dc = DataCollector(max_length=10)
    assert len(dc.data) == 0  # The deque should be empty initially
    assert (
        dc.data.maxlen == 10
    )  # The maximum length of the deque should be as specified


def test_data_collector_callback():
    """
    Test that the data_callback method correctly adds data to the deque.
    """
    dc = DataCollector(max_length=10)
    data = np.array([1, 2, 3])
    dc.data_callback(data)
    assert (
        len(dc.data) == 1
    )  # The deque should contain one item after one call to data_callback
    assert np.array_equal(
        dc.data[0], data
    )  # The item in the deque should be the data that was added


def test_data_collector_overflow():
    """
    Test that when more data is added to the deque than its maximum length,
    the oldest data is correctly removed.
    """
    dc = DataCollector(max_length=10)
    for i in range(15):
        dc.data_callback(np.array([i]))
    assert (
        len(dc.data) == 10
    )  # The deque should not contain more than its maximum length of items
    assert np.array_equal(
        dc.data[0], np.array([5])
    )  # The oldest item should have been removed


@pytest.mark.parametrize("max_length", [-1, 0, "ten", None])
def test_data_collector_invalid_max_length(max_length: Any):
    """
    Test that a ValueError or TypeError is raised when an invalid maximum length
    is passed to the DataCollector constructor.

    Args:
        max_length (Any): The maximum length to test.
    """
    with pytest.raises((ValueError, TypeError)):
        DataCollector(max_length=max_length)


if __name__ == "__main__":
    pytest.main()
