# Standard library imports
from queue import Queue
from threading import Thread
from unittest.mock import MagicMock

# Related third party imports
import pytest
from _pytest.logging import LogCaptureFixture

# Local application/library specific imports
from spectrostaff.broadcasting import Broadcaster, Listener


def test_register() -> None:
    """
    Test that a listener can be registered to the broadcaster.
    """
    broadcaster = Broadcaster()
    listener = Listener(MagicMock())
    broadcaster.register(listener)
    # Check that the listener is in the broadcaster's list of listeners
    assert listener in broadcaster.listeners


def test_broadcast() -> None:
    """
    Test that data is broadcasted to all registered listeners.
    """
    broadcaster = Broadcaster()
    listener1 = Listener(MagicMock())
    listener2 = Listener(MagicMock())
    broadcaster.register(listener1)
    broadcaster.register(listener2)

    data_queue = Queue()
    data_queue.put("Test data")

    # Start broadcasting in a separate thread
    broadcast_thread = Thread(target=broadcaster.broadcast, args=(data_queue,))
    broadcast_thread.start()

    # Give the broadcast thread some time to process the data
    broadcast_thread.join(timeout=0.1)

    # Check that each listener received the broadcasted data
    listener1.data_callback.assert_called_once_with("Test data")
    listener2.data_callback.assert_called_once_with("Test data")

    # Stop broadcasting and wait for the broadcast thread to finish
    broadcaster.stop_broadcasting()
    broadcast_thread.join()


def test_stop_broadcasting() -> None:
    """
    Test that broadcasting can be stopped.
    """
    broadcaster = Broadcaster()
    data_queue = Queue()
    data_queue.put("Test data")

    # Start broadcasting in a separate thread
    broadcast_thread = Thread(target=broadcaster.broadcast, args=(data_queue,))
    broadcast_thread.start()

    # Stop broadcasting
    broadcaster.stop_broadcasting()

    # Wait for the broadcast thread to finish
    broadcast_thread.join()

    # Check that the stop_event was cleared and the broadcast thread is no longer alive
    assert not broadcaster.stop_event.is_set()
    assert not broadcast_thread.is_alive()


def test_receive_data(caplog: LogCaptureFixture) -> None:
    """
    Test the receive_data method of the Listener class.

    This test checks that the receive_data method correctly calls the callback function
    and logs an error message when the callback function raises an exception.

    Args:
        caplog (LogCaptureFixture): Pytest fixture to capture log messages.
    """
    # Create a mock callback function
    mock_callback = MagicMock()

    # Create a Listener object with the mock callback function
    listener = Listener(mock_callback)

    # Define some test data
    test_data = "Test data"

    # Call receive_data with the test data
    listener.receive_data(test_data)

    # Check that the mock callback function was called once with the test data
    mock_callback.assert_called_once_with(test_data)

    # Set the mock callback function to raise an exception when called
    mock_callback.side_effect = Exception("Test exception")

    # Call receive_data again with the test data
    listener.receive_data(test_data)

    # Check that the correct error message was logged
    assert f"An error occurred: Test exception" in caplog.text


if __name__ == "__main__":
    pytest.main()
