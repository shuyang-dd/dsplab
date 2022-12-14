from filter.echo import *
from filter.alien import *
from filter.man import *
from filter.woman import *
from filter.robot import *

from gui import GUI
import wave
import pyaudio
import struct
import numpy as np
import threading

from Transcripter import Transcripter
import asyncio

CHANNELS = 1
RATE = 16000

BLOCKLEN = 1024
WIDTH = 2


class App:
    def __init__(self):
        self.gui = GUI(self)
        self.ts = Transcripter()

        # mode: 0:stopped 1:input from microphone 2: input from wave file
        self.mode = 0
        self.mode_changed = False

        self.block_len = BLOCKLEN

        self.audio = pyaudio.PyAudio()

        self.set_rate(RATE)

    def set_rate(self, rate):
        self.rate = rate
        self.echo_filter = EchoFilter(rate, self.block_len)
        self.alien_filter = AlienFilter(rate, self.block_len)
        self.robot_filter = RobotFilter(rate, self.block_len)
        self.man_filter = ManFilter(rate, self.block_len)
        self.woman_filter = WomanFilter(rate, self.block_len)

    def update_io(self):
        if self.mode == 0:
            self.stop_audio()
            return

        if self.mode == 1:
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=CHANNELS,
                rate=self.rate,
                input=True,
                output=True)

        if self.mode == 2:
            self.wf = wave.open(self.gui.file_path.get(), 'rb')

            self.set_rate(self.wf.getframerate())

            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=CHANNELS,
                rate=self.rate,
                input=False,
                output=True)

        # save file to filename.
        save_file = self.gui.save_file.get()
        save_name = self.gui.save_name.get()
        if save_file and save_name:
            self.output_wf = wave.open(save_name, 'w')      # wave file
            self.output_wf.setframerate(RATE)
            self.output_wf.setsampwidth(WIDTH)
            self.output_wf.setnchannels(CHANNELS)

    def start(self):

        # async transcripting start.
        self.show_ts()

        while self.gui.is_running():
            if self.mode_changed:
                self.mode_changed = False
                self.update_io()
            if self.mode == 0:
                self.gui.update()
                continue
            elif self.mode == 1:
                input_bytes = self.stream.read(
                    self.block_len, exception_on_overflow=False)
            elif self.mode == 2:
                input_bytes = self.wf.readframes(self.block_len)

            if len(input_bytes) < self.block_len * WIDTH:
                input_bytes = b"\x00" * self.block_len * WIDTH

            input_tuple = struct.unpack('h' * self.block_len, input_bytes)

            output_block = np.array(input_tuple)

            if self.gui.echo_enable.get():
                output_block = self.echo_filter.activate(
                    self.gui, input_tuple)

            if self.gui.robot_enable.get():
                output_block = self.robot_filter.activate(
                    self.gui, input_tuple)

            if self.gui.alien_enable.get():
                output_block = self.alien_filter.activate(
                    self.gui, input_tuple)

            if self.gui.man_enable.get():
                output_block = self.man_filter.activate(
                    self.gui, input_tuple)

            if self.gui.woman_enable.get():
                output_block = self.woman_filter.activate(
                    self.gui, input_tuple)

            # spectrum graph
            if self.gui.show_spectrum:
                X = np.fft.fft(input_tuple, norm="ortho") / self.rate
                Y = np.fft.fft(output_block, norm="ortho") / self.rate

                self.gui.spectrum_x.set_ydata(np.abs(X))
                self.gui.spectrum_y.set_ydata(np.abs(Y))

            # wave graph
            if self.gui.show_wave:
                self.gui.wave_x.set_ydata(input_tuple)
                self.gui.wave_y.set_ydata(output_block)

            output_block = np.clip(output_block, -32768, 32767)

            binary_data = struct.pack('h' * self.block_len, *output_block)
            self.stream.write(binary_data)

            if hasattr(self, 'output_wf') and self.output_wf:
                self.output_wf.writeframes(binary_data)

            self.gui.update()

        self.stop_audio()
        self.audio.terminate()

    def stop_audio(self):
        if hasattr(self, 'wf') and self.wf:
            self.wf.close()
            self.wf = None
        if hasattr(self, 'output_wf') and self.output_wf:
            self.output_wf.close()
            self.output_wf = None
        if hasattr(self, 'stream'):
            self.stream.stop_stream()
            self.stream.close()

    def change_mode(self, mode):
        self.mode_changed = True
        self.mode = mode

    def show_ts(self):
        func = self.ts.send_receive()
        new_loop = asyncio.new_event_loop()
        t = threading.Thread(target=self.get_loop, args=(new_loop,))
        t.start()

        asyncio.run_coroutine_threadsafe(func, new_loop)

    def get_loop(self, loop):
        self.loop = loop
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()


app = App()
app.start()
