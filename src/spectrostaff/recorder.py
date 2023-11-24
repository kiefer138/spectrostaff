# Standard library imports
import logging
import queue

# Related third party imports
import pyaudio
from PyQt6.QtCore import pyqtSignal, QMutex, QMutexLocker, QObject

# Local application/library specific imports
from typing import Optional


class Recorder(QObject):
    """
    The Recorder class is responsible for recording audio.

    This class uses a separate thread to record audio and put the audio frames into a queue.

    Attributes:
        stop_event (threading.Event): An event that signals the recording to stop.
        chunk (int): The number of audio frames per buffer.
        channels (int): The number of channels.
        rate (int): The sampling rate.
        frames (queue.Queue): A queue to store the audio frames.
        audio (pyaudio.PyAudio): The PyAudio object.
        stream (Optional[pyaudio.Stream]): The audio stream.

    Methods:
        start_recording(): Starts recording audio.
        stop_recording(): Stops recording audio.
        close(): Closes the audio stream and terminates the PyAudio object.
    """

    def __init__(
        self,
        chunk: int = 1024,
        channels: int = 1,
        rate: int = 44100,
    ):
        """
        Initializes a new instance of the Recorder class.

        Args:
            chunk (int): The number of audio frames per buffer.
            channels (int): The number of channels.
            rate (int): The sampling rate.
        """
        # Event to signal the broadcaster to start
        self.recording_started = pyqtSignal()

        # Boolean flag to indicate whether recording is in progress
        self.recording = False

        # The number of audio frames per buffer
        self.chunk = chunk

        # The number of channels
        self.channels = channels

        # The sampling rate
        self.rate = rate

        # Queue to store the audio frames
        # We use a queue.Queue here because it is thread-safe. This means that multiple threads can add and remove items from the queue without causing any race conditions. This is important because we have multiple threads interacting with this queue: one thread is adding new frames to the queue, and another thread is removing frames from the queue to process them.
        self.frames: queue.Queue = queue.Queue()

        # PyAudio object
        self.audio = pyaudio.PyAudio()

        # Audio stream
        self.stream: Optional[pyaudio.Stream] = None

        # Mutex for thread-safe access to self.recording
        self.recording_mutex = QMutex()

    def start_recording(self) -> None:
        """
        Starts recording audio.

        This method runs in a loop until the stop_event is set. In each iteration of the loop, it reads data from the audio stream and puts it into the frames queue.
        """
        # If already recording, log a message and return
        with QMutexLocker(self.recording_mutex):
            if self.recording:
                logging.info("Recording is already in progress")
                return
            self.recording = True

        try:
            # Open the audio stream
            # We use a try/except block here because opening the audio stream can raise an IOError if the requested audio device is unavailable or if the requested settings are not supported by the device.
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk,
            )

            # If the stream is not None and not active, start it
            if self.stream is not None:
                self.stream.start_stream()

            # Log that recording has started
            logging.info("Recording started")

            # Set the recording flag to True
            self.recording = True

            # Run in a loop until the stop event is set
            while self.recording:
                # Read data from the audio stream
                data = self.stream.read(self.chunk)

                # Put the data into the frames queue
                self.frames.put(data)

        # If an IOError occurs, log it
        # An IOError can occur if the requested audio device is unavailable or if the requested settings are not supported by the device.
        except IOError as e:
            logging.error(f"Error occurred while recording: {e}")

        # Stop the audio stream
        # We use a finally block to ensure that the stream is always closed, even if an error occurs. This is important to prevent resource leaks.
        finally:
            if self.stream is not None:
                # self.stream.stop_stream()
                self.stream.stop_stream()
            self.recording = False  # Set the recording flag to False
            logging.info("Recording stopped")

    def stop_recording(self) -> None:
        """
        Stops recording audio.

        This method sets the stop_event, which signals the recording thread to stop.
        """
        # Set the stop event to signal the recording thread to stop
        with QMutexLocker(self.recording_mutex):
            self.recording = False

        # Log that stop recording was requested
        logging.info("Stop recording requested")

    def close(self) -> None:
        """
        Closes the audio stream and terminates the PyAudio object.

        This method first checks if a recording is in progress. If it is, it stops the recording and then closes the stream.
        Then, it terminates the PyAudio object to free up any system resources used by it.

        Note: This method should be called when you're done using the Recorder object to ensure proper cleanup of resources.
        """
        # If a recording is in progress, stop it
        if self.recording:
            self.stop_recording()

        # If the audio stream is open, close it
        if self.stream is not None:
            self.stream.close()

        # Terminate the PyAudio object
        self.audio.terminate()
