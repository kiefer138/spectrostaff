# Standard library imports
from unittest.mock import Mock, call

# Third-party imports
import pytest
from PyQt6.QtCore import QThread

# Local application/library specific imports
from spectrostaff.gui import RecorderThread  # type: ignore


def test_recorder_thread():
    """
    Test the RecorderThread class.

    This test creates a mock Recorder object and a RecorderThread with the mock Recorder.
    It starts the thread and checks that the thread is running and that start_recording was called.
    Then it stops the thread and checks that stop_recording was called and that the thread is no longer running.
    """
    # Create a mock Recorder object
    mock_recorder = Mock()

    # Create the RecorderThread with the mock Recorder
    thread = RecorderThread(mock_recorder)

    # Start the thread
    thread.start()

    # Give the thread some time to start
    QThread.sleep(1)

    # Check that start_recording was called
    mock_recorder.start_recording.assert_called_once()

    # Stop the thread
    thread.stop()

    # Check that stop_recording was called and that the thread is no longer running
    mock_recorder.stop_recording.assert_called_once()
    assert not thread.isRunning()


if __name__ == "__main__":
    pytest.main()
