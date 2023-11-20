# Standard library imports
import threading
from unittest.mock import patch, MagicMock

# Related third party imports
import pytest
import pyaudio

# Local application/library specific imports
from spectrostaff.recorder import Recorder


@patch("spectrostaff.recorder.pyaudio.PyAudio")
def test_start_recording(mock_pyaudio: MagicMock) -> None:
    """
    Test the start_recording method of the Recorder class.

    This test checks that the PyAudio.open method is called with the correct parameters,
    and that data is read from the stream and put into the frames queue.
    """

    # Create a mock stream object
    mock_stream = MagicMock()

    # Set up the mock PyAudio object to return the mock stream when open is called
    mock_pyaudio.return_value.open.return_value = mock_stream

    # Set up the mock stream to return a specific byte string when read is called
    mock_stream.read.return_value = b"\x00\x00"

    # Create a Recorder object
    recorder = Recorder()

    # Start recording in a separate thread
    recording_thread = threading.Thread(target=recorder.start_recording)
    recording_thread.start()

    # Check that PyAudio.open was called with the correct arguments
    mock_pyaudio.return_value.open.assert_called_once_with(
        format=pyaudio.paInt16,
        channels=recorder.channels,
        rate=recorder.rate,
        input=True,
        frames_per_buffer=recorder.chunk,
    )

    # Check that data was read from the stream and put into the frames queue
    assert recorder.frames.get() == b"\x00\x00"

    # Stop the recording
    recorder.stop_recording()

    # Wait for the recording thread to finish
    recording_thread.join()

    # Check that the stream's stop_stream method was called
    mock_stream.stop_stream.assert_called_once()


def test_stop_recording():
    """
    Test the stop_recording method of the Recorder class.

    This test checks that the stop_event is set when the stop_recording method is called.
    """

    # Create a Recorder object
    recorder = Recorder()

    # Clear the stop_event to ensure it's not set from a previous operation
    recorder.stop_event.clear()

    # Call the stop_recording method, which should set the stop_event
    recorder.stop_recording()

    # Check that the stop_event is set, indicating that the recording has been stopped
    assert recorder.stop_event.is_set()


@patch("spectrostaff.recorder.pyaudio.PyAudio")
def test_close(mock_pyaudio: MagicMock) -> None:
    """
    Test the close method of the Recorder class.

    This test checks that the stream's close method and PyAudio's terminate method are called when the close method is called.
    """

    # Create a mock stream object
    mock_stream = MagicMock()

    # Set up the mock PyAudio object to return the mock stream when open is called
    mock_pyaudio.return_value.open.return_value = mock_stream

    # Create a Recorder object
    recorder = Recorder()

    # Assign the mock stream to the recorder's stream attribute
    recorder.stream = mock_stream

    # Call the close method, which should close the stream and terminate PyAudio
    recorder.close()

    # Check that the stream's close method was called
    mock_stream.close.assert_called_once()

    # Check that PyAudio's terminate method was called
    mock_pyaudio.return_value.terminate.assert_called_once()


# Run the tests if this script is run directly
if __name__ == "__main__":
    pytest.main()
