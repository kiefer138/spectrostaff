# Standard library imports
from __future__ import annotations
import logging
import queue
from typing import Callable, List

# Related third party imports
import numpy as np
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QMutex, QObject


class Broadcaster(QObject):
    """
    The Broadcaster class is responsible for broadcasting data to all registered listeners.
    """

    # Define a PyQt signal that will be emitted when data is ready to be broadcasted
    data_signal: pyqtSignal = pyqtSignal(np.ndarray)

    def __init__(self):
        """
        Initializes a new instance of the Broadcaster class.
        """
        # Call the QObject's initializer
        super().__init__()

        # Initialize broadcasting flag and listeners list
        self.broadcasting = False
        self.listeners: List[Listener] = []

    def register(self, listener: Listener) -> None:
        """
        Registers a listener to receive broadcasted data.

        Args:
            listener (Listener): The listener to register.
        """
        # Attempt to add the listener to the listeners list
        self.listeners.append(listener)

    def broadcast(self, data_queue: queue.Queue) -> None:
        """
        Broadcasts data from the provided queue to all registered listeners in a separate thread.

        Args:
            data_queue (Queue): The queue to get data from.
        """
        # Log the start of broadcasting
        logging.info("Broadcasting started")
        # Set the broadcasting flag to True
        self.broadcasting = True
        # Start a loop that continues until broadcasting is stopped
        while self.broadcasting:
            try:
                # Try to get data from the queue, waiting up to 1 second
                data = data_queue.get(timeout=1)
                # Convert the pyaudio.paInt16 data to a numpy.ndarray of int values
                data = np.frombuffer(data, dtype=np.int16)
                # Emit the data to all listeners
                self.data_signal.emit(data)  # type: ignore
            except queue.Empty:
                # If the queue is empty, break the loop
                break
            except Exception as e:
                # If any other error occurs, log it and continue
                logging.error(f"Error broadcasting data: {e}")

    def stop_broadcasting(self) -> None:
        """
        Stops broadcasting data.
        """
        # Set the broadcasting flag to False to stop the broadcasting loop
        self.broadcasting = False
        # Log that the broadcasting has stopped
        logging.info("Broadcasting stopped")


class Listener(QObject):
    """
    A class that listens for data and processes it in a separate thread.

    The Listener class uses a callback function to process incoming data.
    The data processing function is provided as a callback function when the Listener is created.

    Attributes:
        data_callback (Callable[[np.ndarray], None]): The callback function that processes the data.

    Methods:
        receive_data(data: np.ndarray): Receives data and processes it using the callback function.
    """

    def __init__(self, data_callback: Callable[[np.ndarray], None]):
        """
        Initializes a new Listener object.

        Args:
            data_callback (Callable[[Any], None]): The callback function that processes the data.
        """
        # Call the QObject's initializer
        super().__init__()

        # Store the callback function that will be used to process the data
        self.data_callback = data_callback

    @pyqtSlot(np.ndarray)
    def receive_data(self, data: np.ndarray) -> None:
        """
        Receives data and processes it using the callback function.

        Args:
            data (np.ndarray): The data to be processed.
        """
        try:
            # Process the data using the callback function
            self.data_callback(data)
        except Exception as e:
            # If an error occurs while processing the data, log the error
            logging.error(f"An error occurred in the listener: {e}")
