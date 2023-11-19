import pyaudio
import queue
import threading
import time


class Recorder:
    def __init__(
        self,
        chunk: int = 1024,
        channels: int = 1,
        rate: int = 44100,
    ):
        self.stop_event = threading.Event()
        self.chunk = chunk
        self.channels = channels
        self.rate = rate
        self.frames = queue.Queue()
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.duration = 0

    def start_recording(self):
        """
        audio producer (recorder)
        """
        self.stop_event.clear()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
        )
        print("Recording started")
        while not self.stop_event.is_set():
            data = self.stream.read(self.chunk)
            self.frames.put(data)
        self.stream.stop_stream()

    def stop_recording(self):
        self.stop_event.set()
        print("Recording stopped")

        # signal = np.hstack(
        #     [
        #         np.fromstring(self.frames.get(), dtype=np.int16)
        #         for _ in range(len(self.frames.queue))
        #     ]
        # )
        # time = np.arange(0, len(signal)) * self.chunk / self.rate
        # np.savez("signal.npz", signal=signal, time=time)

        # fig = plt.figure()
        # plt.grid(visible=True)
        # plt.plot(time, signal, "k-", linewidth=0.075)
        # plt.xlabel("Time [s]")
        # plt.ylabel("Amplitude")
        # plt.show()
        # fig.savefig("signal.png")
        # self.audiolot_fourier_transform("signal.npz")

    # def plot_fourier_transform(self, filename):
    #     # Load the array
    #     with np.load(filename) as data:
    #         signal = data["signal"]

    #     samples = len(signal)

    #     # Perform the Fourier transform
    #     fft_array = np.fft.fft(signal)

    #     # Generate frequencies
    #     freq = np.fft.fftfreq(samples, 1 / self.rate)

    #     # Plot the result
    #     fig = plt.figure()
    #     plt.grid(visible=True)
    #     plt.plot(
    #         freq[: samples // 2],
    #         np.abs(fft_array)[: samples // 2],
    #         "k-",
    #         linewidth=0.075,
    #     )
    #     plt.xlabel("Frequency [Hz]")
    #     plt.ylabel("Amplitude")
    #     plt.xlim(30, 1500)
    #     plt.show()
    #     fig.savefig("spectrum.png")
