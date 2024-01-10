# Standard library imports
import threading
import time
from unittest.mock import patch, MagicMock

# Related third party imports
import pytest
import pyaudio

# Local application/library specific imports
from spectrostaff.recorder import Recorder # type: ignore


def test_recorder_initialization() -> None:
    """
    Test the initialization of the Recorder class.

    This test checks that a Recorder object is properly initialized with the correct default values.
    """
    # Create a Recorder object
    recorder = Recorder()

    # Check that the recording flag is False
    assert recorder.recording == False

    # Check that the chunk size is 1024
    assert recorder.chunk == 1024

    # Check that the number of channels is 1
    assert recorder.channels == 1

    # Check that the rate is 44100
    assert recorder.rate == 44100

    # Check that the frames queue is empty
    assert recorder.frames.empty()

    # Check that the audio object is a PyAudio instance
    assert isinstance(recorder.audio, pyaudio.PyAudio)

    # Check that the stream is None
    assert recorder.stream is None


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

    # Check that the recording flag is True
    assert recorder.recording

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

    # Simulate an IOError
    recorder.stream.read.side_effect = IOError("Test error")

    # Wait for the thread to encounter the IOError
    time.sleep(1)

    # Check that the audio stream was stopped
    recorder.stream.stop_stream.assert_called()

    # Check that recording is False
    assert recorder.recording == False


@patch("spectrostaff.recorder.pyaudio.PyAudio")
def test_stop_recording(mock_pyaudio: MagicMock) -> None:
    """
    Test the stop_recording method of the Recorder class.

    This test checks that the stop_recording method properly stops the recording, sets the recording flag to False,
    and stops and closes the audio stream.
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

    # Wait for the recording to start
    time.sleep(1)

    # Assert that the recording flag is True
    assert recorder.recording

    # Call stop_recording
    recorder.stop_recording()

    # Wait for the recording to stop
    time.sleep(1)

    # Check that the recording flag is now False
    assert not recorder.recording

    # Check that the audio stream was stopped
    recorder.stream.stop_stream.assert_called()


def test_close() -> None:
    """
    Test the close method of the Recorder class.

    This test checks that the close method properly closes the audio stream and terminates the PyAudio object.
    """
    # Create a Recorder object
    recorder = Recorder()

    # Mock the PyAudio object and the audio stream
    recorder.audio = MagicMock()
    recorder.stream = MagicMock()

    # Call the close method
    recorder.close()

    # Check that the stream's close method was called
    recorder.stream.close.assert_called_once()

    # Check that the PyAudio object's terminate method was called
    recorder.audio.terminate.assert_called_once()


def test_start_recording_while_already_recording() -> None:
    """
    Test the start_recording method of the Recorder class when a recording is already in progress.

    This test checks that if start_recording is called while a recording is already in progress,
    the method does not start a new recording.
    """
    # Create a Recorder object
    recorder = Recorder()

    # Mock the PyAudio object and the audio stream
    recorder.audio = MagicMock()
    recorder.stream = MagicMock()

    # Start recording
    recorder.recording = True

    # Call start_recording again
    recording_thread = threading.Thread(target=recorder.start_recording)
    recording_thread.start()

    # Check that the PyAudio object's open method was not called
    recorder.audio.open.assert_not_called()


def test_start_recording_while_recording() -> None:
    """
    Test the start_recording method of the Recorder class while a recording is in progress.

    This test checks that if start_recording is called while a recording is already in progress, the method logs a message and returns without starting a new recording.
    """
    # Create a Recorder object
    recorder = Recorder()

    # Mock the PyAudio object and the audio stream
    recorder.audio = MagicMock()
    recorder.stream = MagicMock()

    # Set the recording flag to True to simulate a recording in progress
    recorder.recording = True

    # Call the start_recording method
    with patch("logging.info") as mock_info:
        recorder.start_recording()

    # Check that the logging message was called
    mock_info.assert_called_once_with("Recording is already in progress")

    # Check that the stream's start_stream method was not called
    recorder.stream.start_stream.assert_not_called()


def test_stop_recording_before_start_recording() -> None:
    """
    Test the stop_recording method of the Recorder class when no recording is in progress.

    This test checks that if stop_recording is called before start_recording, the method does not cause any errors.
    """
    # Create a Recorder object
    recorder = Recorder()

    # Mock the PyAudio object and the audio stream
    recorder.audio = MagicMock()
    recorder.stream = MagicMock()

    # Call stop_recording before start_recording
    recorder.stop_recording()

    # Check that the stream's stop_stream and close methods were not called
    recorder.stream.stop_stream.assert_not_called()
    recorder.stream.close.assert_not_called()

    # Check that the recording flag is False
    assert not recorder.recording


def test_close_while_recording() -> None:
    """
    Test the close method of the Recorder class while a recording is in progress.

    This test checks that if close is called while a recording is in progress, the recording is stopped, the stream is closed, and the PyAudio object is terminated.
    """
    # Create a Recorder object
    recorder = Recorder()

    # Mock the PyAudio object and the audio stream
    recorder.audio = MagicMock()
    recorder.stream = MagicMock()

    # Set the recording flag to True to simulate a recording in progress
    recorder.recording = True

    # Call the close method
    recorder.close()

    # Check that the recording flag is now False
    assert not recorder.recording

    # Check that the stream's close method was called
    recorder.stream.close.assert_called_once()

    # Check that the PyAudio object's terminate method was called
    recorder.audio.terminate.assert_called_once()


def test_close_before_start_recording() -> None:
    """
    Test the close method of the Recorder class when no recording is in progress.

    This test checks that if close is called before start_recording, the method does not cause any errors and the PyAudio object is terminated.
    """
    # Create a Recorder object
    recorder = Recorder()

    # Mock the PyAudio object
    recorder.audio = MagicMock()

    # Call the close method
    recorder.close()

    # Check that the PyAudio object's terminate method was called
    recorder.audio.terminate.assert_called_once()

    # Check that the recording flag is False
    assert not recorder.recording


if __name__ == "__main__":
    pytest.main()
