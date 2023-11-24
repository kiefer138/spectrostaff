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

    def __init__(self, max_queue_size: int = 1000):
        """
        Initializes a new instance of the Broadcaster class.
        """
        # Call the QObject's initializer
        super().__init__()

        # Initialize broadcasting flag and listeners list
        self.broadcasting = False
        self.listeners: List[Listener] = []
        self.max_queue_size = max_queue_size

    def register(self, listener: Listener) -> None:
        """
        Registers a listener to receive broadcasted data.

        Args:
            listener (Listener): The listener to register.
        """
        # Attempt to add the listener to the listeners list
        self.listeners.append(listener)

    def unregister(self, listener: Listener) -> None:
        """
        Unregister a listener from the broadcaster.

        This method removes a listener from the broadcaster's list of listeners,
        which means the listener will no longer receive data from the broadcaster.

        Args:
            listener (Listener): The listener to unregister.
        """
        # Check if the listener is in the list of listeners
        if listener in self.listeners:
            # If it is, remove it
            self.listeners.remove(listener)

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
                if data_queue.qsize() > self.max_queue_size:
                    logging.warning("Data queue is full. Dropping data.")
                    while data_queue.qsize() > self.max_queue_size:
                        data_queue.get()
                # Try to get data from the queue, waiting up to 1 second
                # The timeout is used to prevent the thread from blocking indefinitely
                # if there's no data in the queue. This allows the thread to check
                # the broadcasting flag and potentially exit the loop even if there's
                # no data to broadcast.
                data = data_queue.get(timeout=1)
                # Convert the pyaudio.paInt16 data to a numpy.ndarray of int values
                data = np.frombuffer(data, dtype=np.int16)
                # Emit the data to all listeners
                # The 'type: ignore' comment is used to tell the type checker to ignore this line.
                # This is because the type checker may not understand the type of 'self.data_signal.emit(data)'
                # and could raise an error or warning, even though the code is correct.
                self.data_signal.emit(data)  # type: ignore
            except queue.Empty:
                # Log a message and continue with the next iteration
                logging.info("Data queue is currently empty. Waiting for data.")
                continue
            except Exception as e:
                # If any other error occurs, log it and continue
                logging.error(f"Error broadcasting data: {e}")
        self.broadcasting = False
        logging.info("Broadcasting stopped")

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
            data_callback (Callable[[np.ndarray], None]): The callback function that processes the data.
        """
        # Call the QObject's initializer
        super().__init__()

        # Store the callback function that will be used to process the data
        self.data_callback: Callable[[np.ndarray], None] = data_callback

    @pyqtSlot(np.ndarray)
    def receive_data(self, data: np.ndarray) -> None:
        """
        Receives data and processes it using the callback function.

        Args:
            data (np.ndarray): The data to be processed.
        """
        if data.size > 0:
            try:
                # Process the data using the callback function
                # The callback function is expected to perform some kind of processing on the data
                # In this case, the callback function adds the data to a deque for further processing
                # This could include tasks such as filtering the data, performing calculations on it,
                # or storing it for later use.
                self.data_callback(data)
            except Exception as e:
                # If an error occurs while processing the data, log the error
                logging.error(f"An error occurred in the listener: {e}")
        else:
            logging.warning("Received empty data")
