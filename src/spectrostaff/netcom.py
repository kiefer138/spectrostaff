from __future__ import annotations

import queue
import threading

from typing import List


class Broadcaster:
    """
    The Broadcaster class encapsulates the functionality for broadcasting data over a socket.

    Attributes:
        stop_event (threading.Event): An event that signals the broadcasting to stop.
    """

    def __init__(self):
        self.stop_event = threading.Event()
        self.listeners: List[Listener] = []

    def register(self, listener: Listener):
        self.listeners.append(listener)

    def broadcast(self, data_queue: queue.Queue):
        """
        Broadcasts data from the provided queue over a socket.
        """
        self.stop_event.clear()
        print("Broadcasting started")
        while not self.stop_event.is_set():
            try:
                data = data_queue.get_nowait()
            except queue.Empty:
                continue
            if data:
                for listener in self.listeners:
                    listener.receive_data(data)

    def stop_broadcasting(self):
        self.stop_event.set()
        print("Broadcasting stopped")


class Listener:
    def __init__(self, data_callback):
        self.data_callback = data_callback

    def receive_data(self, data):
        threading.Thread(target=self.data_callback, args=(data,)).start()
