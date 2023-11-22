# Standard library imports
import queue
import threading
from unittest.mock import MagicMock

# Related third party imports
import pytest
import numpy as np
from _pytest.logging import LogCaptureFixture
from PyQt6.QtTest import QSignalSpy

# Local application/library specific imports
from spectrostaff.broadcasting import Broadcaster, Listener


def test_broadcaster_initialization() -> None:
    """
    Test the initialization of the Broadcaster class.

    This test checks that a Broadcaster object is properly initialized with the correct default values.
    """
    # Create a Broadcaster object
    broadcaster = Broadcaster()

    # Check that the broadcasting flag is False
    assert broadcaster.broadcasting == False

    # Check that the listeners list is empty
    assert broadcaster.listeners == []

    # Check that the max_queue_size is 1000
    assert broadcaster.max_queue_size == 1000


def test_register() -> None:
    """
    Test the register method of the Broadcaster class.

    This test checks that a Listener object is properly registered.
    """
    # Create a mock callback function
    mock_callback = MagicMock()

    # Create a Listener object with the mock callback function
    listener = Listener(mock_callback)

    # Create a Broadcaster object
    broadcaster = Broadcaster()

    # Register the listener
    broadcaster.register(listener)

    # Check that the listener is in the broadcaster's list of listeners
    assert listener in broadcaster.listeners


def test_unregister() -> None:
    """
    Test the unregister method of the Broadcaster class.

    This test checks that a Listener object is properly unregistered.
    """
    # Create a mock callback function
    mock_callback = MagicMock()

    # Create a Listener object with the mock callback function
    listener = Listener(mock_callback)

    # Create a Broadcaster object and register the listener
    broadcaster = Broadcaster()
    broadcaster.register(listener)

    # Unregister the listener
    broadcaster.unregister(listener)

    # Check that the listener is not in the broadcaster's list of listeners
    assert listener not in broadcaster.listeners


def test_broadcast() -> None:
    """
    Test the broadcast method of the Broadcaster class.

    This test checks that if broadcast is called with a queue containing some data, the method broadcasts the data to all registered listeners.
    """
    # Create a Broadcaster object
    broadcaster = Broadcaster()

    # Create a QSignalSpy to spy on the data_signal of the broadcaster
    spy = QSignalSpy(broadcaster.data_signal)

    # Create a queue and put some mock data in it
    data_queue = queue.Queue()
    mock_data = np.array([1, 2, 3, 4, 5], dtype=np.int16)
    data_queue.put(mock_data.tobytes())

    # Create a thread to run the broadcast method
    broadcast_thread = threading.Thread(
        target=broadcaster.broadcast, args=(data_queue,)
    )

    # Start the thread
    broadcast_thread.start()

    # Wait for the thread to finish
    broadcast_thread.join()

    # Check that the data_signal was emitted once
    assert len(spy) == 1

    # Check that the data_signal was emitted with the mock data
    assert np.array_equal(spy[0][0], mock_data)


def test_stop_broadcasting() -> None:
    """
    Test the stop_broadcasting method of the Broadcaster class.

    This test checks that if stop_broadcasting is called, the broadcasting attribute is set to False.
    """
    # Create a Broadcaster object
    broadcaster = Broadcaster()

    # Set the broadcasting attribute to True
    broadcaster.broadcasting = True

    # Call the stop_broadcasting method
    broadcaster.stop_broadcasting()

    # Check that the broadcasting attribute is False
    assert broadcaster.broadcasting == False


def test_receive_data() -> None:
    """
    Test the receive_data method of the Listener class.

    This test checks that if receive_data is called with some data, the method processes the data using the callback function.
    """
    # Create a mock callback function
    mock_callback = MagicMock()

    # Create a Listener object with the mock callback function
    listener = Listener(mock_callback)

    # Create some mock data
    mock_data = np.array([1, 2, 3, 4, 5], dtype=np.int16)

    # Call the receive_data method with the mock data
    listener.receive_data(mock_data)

    # Check that the mock callback function was called with the mock data
    mock_callback.assert_called_once_with(mock_data)


def test_receive_data_empty_array() -> None:
    """
    Test the receive_data method of the Listener class.

    This test checks that if receive_data is called with an empty numpy array, the method does not call the callback function.
    """
    # Create a mock callback function
    mock_callback = MagicMock()

    # Create a Listener object with the mock callback function
    listener = Listener(mock_callback)

    # Create an empty numpy array
    empty_data = np.array([], dtype=np.int16)

    # Call the receive_data method with the empty array
    listener.receive_data(empty_data)

    # Check that the mock callback function was not called
    mock_callback.assert_not_called()


if __name__ == "__main__":
    pytest.main()
