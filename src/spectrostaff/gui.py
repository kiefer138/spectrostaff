import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import threading

from collections import deque

from netcom import Broadcaster, Listener
from recorder import Recorder


class DataCollector:
    def __init__(self, max_length: int):
        self.data = deque(maxlen=max_length)

    def data_callback(self, data):
        self.data.append(data)


class AudioGUI:
    def __init__(self, master: tk.Tk):
        self.master = master
        # Bind the window's close event to the cleanup method
        self.master.protocol("WM_DELETE_WINDOW", self.close)
        self.broadcaster = Broadcaster()
        self.recorder = Recorder()
        self.data_collector = DataCollector(self.recorder.chunk)

        # Create Listener and register it with the Broadcaster
        self.listener = Listener(self.data_collector.data_callback)
        self.broadcaster.register(self.listener)

        # Create start and stop buttons
        self.start_button = tk.Button(master, text="Start", command=self.start)
        self.start_button.pack()
        self.stop_button = tk.Button(master, text="Stop", command=self.stop)
        self.stop_button.pack()
        self.close_button = tk.Button(master, text="Close", command=self.close)
        self.close_button.pack()

        # Create a figure for the plot
        self.fig = Figure(figsize=(5, 4), dpi=200)
        self.ax = self.fig.add_subplot(111)

        # Add a grid
        self.ax.grid(True, color="b", linewidth=0.1)

        # Initialize the line object for the plot
        (self.line,) = self.ax.plot([], [], color="magenta", linewidth=0.1)

        # Set up the plot
        self.ax.set_xlim(
            0, self.recorder.chunk / self.recorder.rate
        )  # chunk is the number of data points to display at a time
        self.ax.set_ylim(-32768, 32767)  # 16-bit audio ranges from -32768 to 32767

        # Set up the x-axis and y-axis labels
        self.ax.set_xlabel("Time [s]")
        self.ax.set_ylabel("Amplitude")
        self.ax.set_title("Real-time Audio Signal")

        # Create a canvas and add it to the window
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def start(self):
        # Start recording thread if it's not already running
        try:
            if (
                not hasattr(self, "recording_thread")
                or not self.recording_thread.is_alive()
            ):
                self.recording_thread = threading.Thread(
                    target=self.recorder.start_recording
                )
                self.recording_thread.start()
        except Exception as e:
            print(f"Error starting recording: {e}")

        # Start broadcasting thread if it's not already running
        try:
            if (
                not hasattr(self, "broadcasting_thread")
                or not self.broadcasting_thread.is_alive()
            ):
                self.broadcasting_thread = threading.Thread(
                    target=self.broadcaster.broadcast, args=(self.recorder.frames,)
                )
                self.broadcasting_thread.start()
        except Exception as e:
            print(f"Error starting broadcasting: {e}")
        # Start the animation
        self.ani = animation.FuncAnimation(
            self.fig, self.plot_audio_signal, interval=100, blit=True
        )

    def stop(self):
        # Stop recording
        self.recorder.stop_recording()

        # Stop the animation
        self.ani.event_source.stop()

    def close(self):
        # Stop all recording and broadcasting threads
        self.recorder.stop_recording()
        self.broadcaster.stop_broadcasting()
        # Join the threads if they exist
        if hasattr(self, "recording_thread") and self.recording_thread is not None:
            self.recording_thread.join()
        if (
            hasattr(self, "broadcasting_thread")
            and self.broadcasting_thread is not None
        ):
            self.broadcasting_thread.join()
        # Destroy the window
        self.master.destroy()

    def plot_audio_signal(self, i=None):
        # Convert the collected data to a numpy array
        audio_data = np.frombuffer(b"".join(self.data_collector.data), dtype=np.int16)
        # start = time.time()
        time_data = np.array([i * self.recorder.chunk / self.recorder.rate for i in range(len(audio_data))])
        
        # Update the line data
        self.line.set_data(time_data, audio_data)

        # Update the x-axis limits to accomodate the new data
        self.ax.set_xlim(time_data[0], time_data[-1])

        return (self.line,)


# Create the GUI
root = tk.Tk()
gui = AudioGUI(root)
root.mainloop()
