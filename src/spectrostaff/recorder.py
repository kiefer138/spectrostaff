# Standard library imports
import logging
import queue
import threading

# Related third party imports
import pyaudio

# Local application/library specific imports
from typing import Optional


class Recorder:
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
        # Event to signal the recording thread to stop
        self.stop_event = threading.Event()

        # The number of audio frames per buffer
        self.chunk = chunk

        # The number of channels
        self.channels = channels

        # The sampling rate
        self.rate = rate

        # Queue to store the audio frames
        self.frames = queue.Queue()

        # PyAudio object
        self.audio = pyaudio.PyAudio()

        # Audio stream
        self.stream: Optional[pyaudio.Stream] = None

    def start_recording(self) -> None:
        """
        Starts recording audio.

        This method runs in a loop until the stop_event is set. In each iteration of the loop, it reads data from the audio stream and puts it into the frames queue.
        """
        # Clear the stop event to allow recording to start
        self.stop_event.clear()

        try:
            # Open the audio stream
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk,
            )

            # Log that recording has started
            logging.info("Recording started")

            # Run in a loop until the stop event is set
            while not self.stop_event.is_set():
                # Read data from the audio stream
                data = self.stream.read(self.chunk)

                # Put the data into the frames queue
                self.frames.put(data)

        # If any exception occurs, log it
        except IOError as e:
            logging.error(f"Error occurred while recording: {e}")

        # Stop the audio stream
        finally:
            if self.stream is not None:
                self.stream.stop_stream()
                self.stream.close()

    def stop_recording(self) -> None:
        """
        Stops recording audio.

        This method sets the stop_event, which signals the recording thread to stop.
        """
        # Set the stop event to signal the recording thread to stop
        self.stop_event.set()

        # Log that recording has stopped
        logging.info("Recording stopped")

    def close(self) -> None:
        """
        Closes the audio stream and terminates the PyAudio object.

        If the audio stream is open, it is closed first. Then, the PyAudio object is terminated.
        """
        # If the audio stream is open, close it
        if self.stream is not None:
            self.stream.close()

        # Terminate the PyAudio object
        self.audio.terminate()
