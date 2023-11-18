import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import socket
import threading
import tkinter as tk

from recorder import Recorder

matplotlib.use("Agg")

recorder = Recorder()


def start_recording():
    recorder.stop_event.clear()
    threading.Thread(target=listen_for_frames).start()
    threading.Thread(target=recorder.start_recording).start()


def listen_for_frames():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = ("localhost", 10000)
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(1)
    while not recorder.stop_event.is_set():
        # Wait for a connection
        print("waiting for a connection")
        connection, client_address = sock.accept()
        signal = []
        print("connection from", client_address)
        try:
            while not recorder.stop_event.is_set():
                data = connection.recv(2048)
                if data:
                    signal.extend(np.frombuffer(data, dtype=np.int16))
                else:
                    break
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            connection.close()
    # Normalize the signal
    normalized_signal = signal / np.max(np.abs(signal))
    time = np.arange(len(signal)) / recorder.rate
    plt.ioff()
    fig = plt.figure(dpi=1200)
    plt.grid(visible=True, linewidth=0.1, color="b")
    plt.plot(time, normalized_signal, "m-", linewidth=0.05)
    plt.title("Microphone signal")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude (a.u.)")
    plt.savefig("signal.png")
    plt.close("all")


def stop_recording():
    recorder.stop_recording()
    root.quit()


def save_audio():
    recorder.save_audio("record.wav")


root = tk.Tk()
frame = tk.Frame(root)
frame.pack()

start_button = tk.Button(frame, text="Start", command=start_recording)
start_button.pack(side=tk.LEFT)

stop_button = tk.Button(frame, text="Stop", command=stop_recording)
stop_button.pack(side=tk.LEFT)


root.mainloop()
