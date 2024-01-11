# Standard library imports
from collections import deque

# Related Third-party imports
import numpy as np
from scipy.fft import fft  # type: ignore
from PyQt6.QtCore import QMutex


class DataCollector:
    """
    A class that collects and stores a fixed amount of data in a thread-safe manner.

    Attributes:
        data (deque): A deque to store the collected data.
        lock (QMutex): A mutex to ensure thread-safety when modifying the deque.
    """

    def __init__(self, max_length: int = 1024):
        """
        Initializes a new DataCollector object.

        Args:
            max_length (int, optional): The maximum size of the deque. Defaults to 100.
        """
        # Check that max_length is a positive integer
        if not isinstance(max_length, int) or max_length <= 0:
            raise ValueError("max_length must be a positive integer")
        # Initialize a deque with a fixed maximum size
        self.data: deque[np.ndarray] = deque(maxlen=max_length)
        # Initialize a mutex for thread-safety
        self.lock = QMutex()

    def data_callback(self, data: np.ndarray) -> None:
        """
        Adds new data to the deque in a thread-safe manner.

        Args:
            data (np.ndarray): The data to add.
        """
        # Acquire the lock before modifying the deque
        self.lock.lock()
        try:
            # Check that the data is a numpy array
            if not isinstance(data, np.ndarray):
                raise ValueError("data must be a numpy array")
            # Add the new data to the deque
            # If the deque is full, the oldest item is automatically removed
            self.data.append(data)
        finally:
            # Always release the lock, even if an error occurred
            self.lock.unlock()


class FFTDataCollector(DataCollector):
    """
    A class that collects and stores a fixed amount of FFT data in a thread-safe manner.
    Inherits from the DataCollector class.

    Attributes:
        freqs (np.ndarray): The frequency bins for the FFT data.
    """

    def __init__(self, max_length: int = 1024, rate: int = 44100, chunk: int = 4410):
        """
        Initializes a new FFTDataCollector object.

        Args:
            max_length (int, optional): The maximum size of the deque. Defaults to 1024.
            rate (int, optional): The sample rate of the data. Defaults to 44100.
            chunk (int, optional): The size of each chunk of data. Defaults to 4410.
        """
        super().__init__(max_length=max_length)
        # Check that rate and chunk are greater than zero
        if rate <= 0 or chunk <= 0:
            raise ValueError("rate and chunk must be greater than zero")
        # Calculate the frequency bins for the FFT data
        self.freqs: np.ndarray = np.fft.fftfreq(chunk, 1 / rate)

    def data_callback(self, data: np.ndarray) -> None:
        """
        Adds new FFT data to the deque in a thread-safe manner.

        Args:
            data (np.ndarray): The data to add.
        """
        # Acquire the lock before modifying the deque
        self.lock.lock()
        try:
            # Check that the data is a numpy array
            if not isinstance(data, np.ndarray):
                raise ValueError("data must be a numpy array")
            # Calculate FFT of the incoming data
            fft_data = fft(data)
            # Add the new FFT data to the deque
            # If the deque is full, the oldest item is automatically removed
            self.data.append(fft_data)
        finally:
            # Always release the lock, even if an error occurred
            self.lock.unlock()
