# Standard library imports
from __future__ import annotations
import logging
import queue
from typing import Optional

# Related third party imports
import numpy as np
import pyqtgraph as pg  # type: ignore
from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal, pyqtSlot, QMutexLocker
from PyQt6.QtGui import QCloseEvent, QTransform
from PyQt6.QtWidgets import (
    QMainWindow,
    QApplication,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QSplitter,
)

# Local application/library specific imports
from spectrostaff.data import DataCollector, FFTDataCollector
from spectrostaff.broadcasting import Broadcaster, Listener
from spectrostaff.recorder import Recorder


class RecorderThread(QThread):
    """
    A class that runs a Recorder in a separate thread.

    Attributes:
        recorder (Recorder): The Recorder to run.
    """

    # Define a PyQt signal that will be emitted when recording starts
    recording_started = pyqtSignal()

    def __init__(self, recorder: Recorder):
        """
        Initializes a new RecorderThread object.

        Args:
            recorder (Recorder): The Recorder to run.
        """
        super().__init__()
        # Store the Recorder
        self.recorder = recorder

    def run(self) -> None:
        """
        Emits the recording_started signal and starts the Recorder.
        """
        # Emit the recording_started signal. This signal is connected to the start method of the BroadcasterThread.
        # When this signal is emitted, it will trigger the start of the BroadcasterThread.
        self.recording_started.emit()

        # Call the start_recording method of the recorder object. This starts the actual recording process.
        self.recorder.start_recording()

    def stop(self) -> None:
        """
        Stops the RecorderThread.
        """
        # Call the stop_recording method of the recorder object.
        # This should stop the recording process.
        self.recorder.stop_recording()

        # Wait for the thread to finish.
        # This is a blocking call which will not return until the thread has completely finished execution.
        self.wait()


class BroadcasterThread(QThread):
    """
    A class that runs a Broadcaster in a separate thread.

    Attributes:
        broadcaster (Broadcaster): The Broadcaster to run.
        frames (queue.Queue): The queue of frames to broadcast.
    """

    def __init__(self, broadcaster: Broadcaster, frames: queue.Queue):
        """
        Initializes a new BroadcasterThread object.

        Args:
            broadcaster (Broadcaster): The Broadcaster to run.
            frames (queue.Queue): The queue of frames to broadcast.
        """
        super().__init__()
        # Store the Broadcaster and the queue of frames
        self.broadcaster = broadcaster
        self.frames = frames

    @pyqtSlot()
    def run(self) -> None:
        """
        Starts the Broadcaster.

        This method is automatically called when the thread's start() method is called.
        It calls the broadcast method of the broadcaster object, passing it the queue of frames.
        """
        # Start the Broadcaster
        self.broadcaster.broadcast(self.frames)

    def stop(self) -> None:
        """
        Stops the BroadcasterThread.

        This method stops the broadcasting by calling the stop_broadcasting method of the broadcaster object.
        It then waits for the thread to finish execution by calling the thread's wait method.
        """
        # Stop the broadcasting
        self.broadcaster.stop_broadcasting()
        # Wait for the thread to finish execution
        self.wait()


class Visualizer(QMainWindow):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initializes a new Visualizer object.

        Args:
            parent (Optional[QWidget], optional): The parent widget. Defaults to None.
        """
        super(Visualizer, self).__init__(parent)

        # Create a DataCollector to collect and store audio data
        self.data_collector = DataCollector()

        # Create a DataCollector to collect and store FFT data
        self.fft_data_collector = FFTDataCollector()

        self.duration = 10  # seconds
        self.rate = 44100  # samples per second
        self.chunk = 2048  # samples per buffer

        # Create a Recorder to record audio data
        self.recorder = Recorder(chunk=self.chunk, rate=self.rate)

        # Create a Broadcaster to broadcast audio data
        self.broadcaster = Broadcaster()

        # Create a Listener to listen for and store audio data
        self.listener = Listener(self.data_collector.data_callback)
        self.broadcaster.register(self.listener)

        # Create a Listener to listen for and store FFT data
        self.fft_listener = Listener(self.fft_data_collector.data_callback)
        self.broadcaster.register(self.fft_listener)

        # Create a RecorderThread and a BroadcasterThread
        self.recorder_thread = RecorderThread(self.recorder)
        self.broadcaster_thread = BroadcasterThread(
            self.broadcaster, self.recorder.frames
        )

        # Connect the recording_started signal to the broadcaster thread's start method
        self.recorder_thread.recording_started.connect(self.broadcaster_thread.start)

        # Connect the data callback to the listener
        self.broadcaster.data_signal.connect(self.listener.receive_data)

        # Connect the data callback to the FFT listener
        self.broadcaster.data_signal.connect(self.fft_listener.receive_data)

        # Create a PlotWidget to display the audio data
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel("left", "Amplitude")
        self.plot_widget.setLabel("bottom", "Time (s)")

        # Get the PlotItem from the PlotWidget
        plot_item = self.plot_widget.getPlotItem()

        # Show the grid
        plot_item.showGrid(x=True, y=True)

        # Fix the y-axis range for a typical int16 audio signal
        plot_item.setRange(yRange=[-1, 1]) # [-32768, 32767])

        self.setCentralWidget(self.plot_widget)

        self.fft_graphics_layout_widget = pg.GraphicsLayoutWidget()

        self.fft_plot_item = pg.PlotItem()
        self.fft_plot_item.setLabels(left="Frequency (Hz)", bottom="Time (s)")

        self.fft_plot_item.showGrid(x=True, y=True)

        self.fft_image_item = pg.ImageItem()
        self.fft_plot_item.addItem(self.fft_image_item)

        tr = QTransform()
        tr.scale(self.chunk / self.rate, 1 / (self.chunk / self.rate))
        self.fft_image_item.setTransform(tr)

        self.fft_graphics_layout_widget.addItem(self.fft_plot_item)

        # Create start and stop buttons
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop)

        # Create a QSplitter to display the plot widget and the buttons
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Add the plot widget and the buttons to the splitter
        splitter.addWidget(self.fft_graphics_layout_widget)
        splitter.addWidget(self.plot_widget)

        # Create a layout and add the plot widget and buttons
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        # Create a central widget and set the layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Create an empty array of audio data
        self.data = np.zeros(self.duration * self.rate, dtype=np.float32)
        self.circular_buffer_index = 0
        self.rel_time = np.arange(len(self.data)) / self.rate  # seconds
        self.curve = self.plot_widget.plot(
            self.rel_time,
            self.data,
            pen=pg.mkPen("m", width=0.5, style=Qt.PenStyle.SolidLine),
        )
        # Create an empty array of FFT data
        self.spectrogram = np.zeros(
            (self.rate // self.chunk * self.duration, self.chunk // 2 + 1)
        )

        # Create a QTimer
        self.timer = QTimer()
        # Connect the timeout signal to update_plot
        self.timer.timeout.connect(self.update_plot)
        # Start the timer with an interval of 100 milliseconds
        self.timer.start(100)

        self.fft_timer = QTimer()
        self.fft_timer.timeout.connect(self.update_fft_plot)
        self.fft_timer.start(100)  # Update every 100 ms

    def start(self) -> None:
        """
        Starts recording and broadcasting audio data.

        If a RecorderThread is not currently running and has finished its previous job, a new one is created.
        A new BroadcasterThread is also created but not started.
        When the RecorderThread starts, it emits a signal that triggers the start of the BroadcasterThread.

        The BroadcasterThread is responsible for broadcasting the audio data from the frames queue of the Recorder.
        The RecorderThread is responsible for recording audio data and adding it to its frames queue.
        """

        # Check if the RecorderThread is not currently running and has finished its previous job
        if self.recorder_thread.isFinished() and self.broadcaster_thread.isFinished():
            # Create a new RecorderThread
            self.recorder_thread = RecorderThread(self.recorder)
            # Create a new BroadcasterThread
            self.broadcaster_thread = BroadcasterThread(
                self.broadcaster, self.recorder.frames
            )
            # Connect the recording_started signal to the broadcaster thread's start method
            # This ensures that the BroadcasterThread starts when the RecorderThread starts
            self.recorder_thread.recording_started.connect(
                self.broadcaster_thread.start
            )

        # If the RecorderThread is not currently running, start it
        if not self.recorder_thread.isRunning():
            self.recorder_thread.start()

    def stop(self) -> None:
        """
        Stops recording and broadcasting audio data.

        If a RecorderThread is currently running, it stops the recording.
        If a BroadcasterThread is currently running, it stops the broadcasting.

        Note: This method should be called when you want to stop recording and broadcasting audio data.
        """

        # If a BroadcasterThread is currently running, stop the broadcasting
        if self.broadcaster_thread.isRunning():
            self.broadcaster_thread.stop()

        # If a RecorderThread is currently running, stop the recording
        if self.recorder_thread.isRunning():
            self.recorder_thread.stop()

    def update_plot(self) -> None:
        """
        Updates the plot with the latest audio data from the data collector.

        This method retrieves new data from the data collector, appends it to the existing data,
        and then updates the plot with the combined data. If the recorder is not currently recording,
        the method simply returns without making any changes.
        """
        # If the recorder is not recording, return without making any changes
        with QMutexLocker(self.recorder.recording_mutex):
            if not self.recorder.recording:
                return

        # Retrieve and append new data from the data collector
        while True:
            try:
                # Retrieve new data from the data collector
                with QMutexLocker(self.data_collector.lock):
                    if len(self.data_collector.data) > 0:
                        new_data = self.data_collector.data.popleft()
                    else:
                        break
            except IndexError:
                # If an IndexError occurs, break the loop
                break

            # Append new data to the existing data
            self.data = np.roll(self.data, -len(new_data))
            self.data[-len(new_data) :] = new_data

        # Update the plot with the combined data
        self.curve.setData(self.rel_time, self.data)

    def update_fft_plot(self) -> None:
        """
        Updates the FFT plot with the latest FFT data from the FFT data collector.

        This method retrieves new FFT data from the FFT data collector, and then updates the FFT plot with the new data.
        If the recorder is not currently recording, the method simply returns without making any changes.
        """
        # If the recorder is not recording, return without making any changes
        with QMutexLocker(self.recorder.recording_mutex):
            if not self.recorder.recording:
                return

        # Retrieve and append new FFT data from the FFT data collector
        while True:
            try:
                # Retrieve new FFT data from the FFT data collector
                with QMutexLocker(self.fft_data_collector.lock):
                    if len(self.fft_data_collector.data) > 0:
                        new_fft_data = self.fft_data_collector.data.popleft()
                    else:
                        break
            except IndexError:
                # If an IndexError occurs, break the loop
                break

            self.spectrogram = np.roll(self.spectrogram, -1, axis=0)
            self.spectrogram[-1, :] = np.abs(new_fft_data[: self.chunk // 2 + 1])

        # Update the ImageView widget with the spectrogram
        self.fft_image_item.setImage(
            20 * np.log10(self.spectrogram + 1e-6),  # Convert to dB
        )

    def closeEvent(self, event: Optional[QCloseEvent]) -> None:
        """
        Handles the event that is triggered when the window is closed.

        This method first stops the recording and broadcasting of audio data.
        Then, it checks if the RecorderThread and BroadcasterThread are running. If they are, it stops them.
        Finally, it accepts the close event to close the window.

        Args:
            event (QCloseEvent): The close event to handle.
        """
        # Stop the recording and broadcasting of audio data
        self.stop()

        # If the RecorderThread is running, stop it
        if hasattr(self, "recorder_thread"):
            self.recorder_thread.quit()
            self.recorder_thread.wait()

        # If the BroadcasterThread is running, stop it
        if hasattr(self, "broadcaster_thread"):
            self.broadcaster_thread.quit()
            self.broadcaster_thread.wait()

        # Accept the close event to close the window
        if event is not None:
            event.accept()


def frequency_to_semitone(freq: float) -> float:
    A4_freq = 440.0  # Hz
    return 12 * np.log2(freq / A4_freq)


def main():
    app = QApplication([])
    visualizer = Visualizer()
    visualizer.show()
    app.exec()


if __name__ == "__main__":
    main()
