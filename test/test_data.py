# Standard library imports
from typing import Any

# Related third-party imports
import numpy as np
import pytest

# Local application/library specific imports
from spectrostaff.data import DataCollector, FFTDataCollector # type: ignore


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


def test_fft_data_collector_initialization():
    """
    Test that an FFTDataCollector object is correctly initialized.
    """
    fdc = FFTDataCollector(max_length=10, rate=44100, chunk=4410)
    assert len(fdc.data) == 0  # The deque should be empty initially
    assert (
        fdc.data.maxlen == 10
    )  # The maximum length of the deque should be as specified
    assert (
        len(fdc.freqs) == 4410
    )  # The freqs array should have the same length as the chunk size


def test_fft_data_collector_callback():
    """
    Test that the data_callback method correctly adds FFT data to the deque.
    """
    fdc = FFTDataCollector(max_length=10, rate=44100, chunk=4410)
    data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    fdc.data_callback(data)
    assert (
        len(fdc.data) == 1
    )  # The deque should contain one item after one call to data_callback


def test_fft_data_collector_overflow():
    """
    Test that when more data is added to the deque than its maximum length,
    the oldest data is correctly removed.
    """
    fdc = FFTDataCollector(max_length=10, rate=44100, chunk=4410)
    for i in range(15):
        fdc.data_callback(np.array([i]))
    assert (
        len(fdc.data) == 10
    )  # The deque should not contain more than its maximum length of items


@pytest.mark.parametrize(
    "max_length, rate, chunk", [(-1, 44100, 4410), (10, -1, 4410), (10, 44100, -1)]
)
def test_fft_data_collector_invalid_parameters(max_length, rate, chunk):
    """
    Test that a ValueError is raised when an invalid parameter is passed to the FFTDataCollector constructor.

    Args:
        max_length (int): The maximum length to test.
        rate (int): The rate to test.
        chunk (int): The chunk size to test.
    """
    with pytest.raises(ValueError):
        FFTDataCollector(max_length=max_length, rate=rate, chunk=chunk)


if __name__ == "__main__":
    pytest.main()
