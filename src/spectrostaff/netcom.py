# Standard library imports
from __future__ import annotations
import queue
import threading
import logging

# Related third party imports
from typing import Callable, Any, List


# Configure logging
logging.basicConfig(level=logging.INFO)


class Broadcaster:
    """
    The Broadcaster class is responsible for broadcasting data to all registered listeners.

    This class uses a separate thread to broadcast data from a queue to all registered listeners.
    Broadcasting can be stopped by calling the `stop_broadcasting` method, which sets an event that signals the broadcasting thread to stop.

    Attributes:
        stop_event (threading.Event): An event that signals the broadcasting to stop.
        listeners (List[Listener]): A list of listeners to broadcast data to.
        lock (threading.Lock): A lock to ensure thread-safety when modifying the listeners list.

    Methods:
        register(listener: Listener): Registers a listener to receive broadcasted data.
        broadcast(data_queue: queue.Queue): Starts broadcasting data from the provided queue to all registered listeners.
        stop_broadcasting(): Stops broadcasting data.
    """

    def __init__(self):
        """
        Initializes a new instance of the Broadcaster class.
        """
        # Event to signal the broadcasting thread to stop
        self.stop_event = threading.Event()

        # List of listeners to broadcast data to
        self.listeners: List[Listener] = []

        # Lock to ensure thread-safety when modifying the listeners list
        self.lock = threading.Lock()

    def register(self, listener: Listener) -> None:
        """
        Registers a listener to receive broadcasted data.

        Args:
            listener (Listener): The listener to register.
        """
        # Acquire the lock to ensure thread-safety when modifying the listeners list
        with self.lock:
            # Append the listener to the listeners list
            self.listeners.append(listener)

    def broadcast(self, data_queue: queue.Queue):
        """
        Broadcasts data from the provided queue to all registered listeners.

        This method runs in a loop until the stop_event is set or the data_queue is empty.
        In each iteration of the loop, it gets data from the queue and sends it to each listener.

        Args:
            data_queue (Queue): The queue to get data from.
        """
        # Clear the stop event to allow broadcasting to start
        self.stop_event.clear()

        # Log that broadcasting has started
        logging.info("Broadcasting started")

        # Run in a loop until the stop event is set
        while not self.stop_event.is_set():
            try:
                # Get data from the queue, blocking until data is available or the timeout is reached
                data = data_queue.get(timeout=1)

                # Acquire the lock to ensure thread-safety when sending data to the listeners
                with self.lock:
                    # Send the data to each listener
                    for listener in self.listeners:
                        listener.receive_data(data)

            # If the queue is empty, break out of the loop
            except queue.Empty:
                break

            # If any other exception occurs, log it and continue with the next iteration
            except Exception as e:
                logging.error(f"Error broadcasting data: {e}")
        self.stop_event.clear()
        logging.info("Broadcasting started")
        while not self.stop_event.is_set():
            try:
                data = data_queue.get(timeout=1)  # Blocks until data is available
                with self.lock:
                    for listener in self.listeners:
                        listener.receive_data(data)
            except queue.Empty:
                break
            except Exception as e:
                logging.error(f"Error broadcasting data: {e}")

    def stop_broadcasting(self) -> None:
        """
        Stops broadcasting data.

        This method sets the stop_event, which signals the broadcasting thread to stop.
        """
        # Set the stop event to signal the broadcasting thread to stop
        self.stop_event.set()

        # Log that broadcasting has stopped
        logging.info("Broadcasting stopped")


class Listener:
    """
    The Listener class is responsible for receiving data and triggering a callback function.

    This class uses a separate thread to run the callback function, allowing it to process data asynchronously.

    Attributes:
        data_callback (Callable[[Any], None]): The callback function to run when data is received.

    Methods:
        receive_data(data: Any): Receives data and starts a new thread to run the callback function with the received data.
    """

    def __init__(self, data_callback: Callable[[Any], None]):
        """
        Initializes a new instance of the Listener class.

        Args:
            data_callback (Callable[[Any], None]): The callback function to run when data is received.
        """
        # The callback function to run when data is received
        self.data_callback = data_callback

    def receive_data(self, data: Any) -> None:
        """
        Receives data and starts a new thread to run the callback function with the received data.

        Args:
            data (Any): The data to process.
        """
        # Start a new thread to run the callback function with the received data
        threading.Thread(target=self.data_callback, args=(data,)).start()
