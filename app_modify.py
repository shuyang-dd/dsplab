# Tk_demo_04_slider.py
# TKinter demo
# Play a sinusoid using Pyaudio. Use two sliders to adjust the frequency and gain.

from effects.echo import *
from effects.vibrato import *
from effects.am import *
from effects.pitchshift import *
from effects.chorus import *

from view import View
import wave
import pyaudio
import struct
import numpy as np
import threading

from Transcripter import Transcripter
import asyncio


CHANNELS = 1
RATE = 16000     # rate (samples/second)
BLOCKLEN = 1024
WIDTH = 2


class App:
    def __init__(self):
        self.view = View(self)
        self.ts = Transcripter()

        self.mode = 0
        self.mode_changed = False

        self.block_len = BLOCKLEN
        self.audio = pyaudio.PyAudio()

        self.set_rate(RATE)

    def set_rate(self, rate):
        self.rate = rate
        self.echo_effect = EchoEffect(rate, self.block_len)
        self.vibrato_effect = VibratoEffect(rate, self.block_len)
        self.am_effect = AMEffect(rate, self.block_len)
        self.pitchshift_effect = PitchShift(rate, self.block_len)
        self.chorus_effect = ChorusEffect(rate, self.block_len)

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
            self.wf = wave.open(self.view.file_path.get(), 'rb')

            self.set_rate(self.wf.getframerate())

            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=CHANNELS,
                rate=self.rate,
                input=False,
                output=True)

        save_file = self.view.save_file.get()
        save_name = self.view.save_name.get()
        if save_file and save_name:
            self.output_wf = wave.open(save_name, 'w')      # wave file
            self.output_wf.setframerate(RATE)
            self.output_wf.setsampwidth(WIDTH)
            self.output_wf.setnchannels(CHANNELS)

    # mode: 0 -- Stopped, 1 -- Microph, 2 -- Wave File
    def start(self):

        self.show_ts()
        s_count = 0
        w_count = 0
        while self.view.is_running():
            if self.mode_changed:
                self.mode_changed = False
                self.update_io()
            if self.mode == 0:
                self.view.update()
                continue
            elif self.mode == 1:
                input_bytes = self.stream.read(
                    self.block_len, exception_on_overflow=False)
            elif self.mode == 2:
                input_bytes = self.wf.readframes(self.block_len)

            if len(input_bytes) < self.block_len * WIDTH:
                input_bytes = b"\x00" * self.block_len * WIDTH

            input_tuple = struct.unpack(
                'h' * self.block_len, input_bytes)  # Convert

            output_block = np.array(input_tuple)

            if self.view.echo_enable.get():
                output_block += self.echo_effect.apply(self.view, input_tuple)

            if self.view.am_enable.get():
                output_block += self.am_effect.apply(self.view, input_tuple)

            if self.view.vibrato_enable.get():
                output_block += self.vibrato_effect.apply(
                    self.view, input_tuple)

            if self.view.pitchshift_enable.get():
                output_block += self.pitchshift_effect.apply(
                    self.view, input_tuple)

            if self.view.chorus_enable.get():
                output_block += self.chorus_effect.apply(
                    self.view, input_tuple)

            # Spectrum Plot
            if self.view.show_spectrum and s_count > 1:
                s_count = 0
                X = np.fft.fft(input_tuple, norm="ortho") / self.rate
                Y = np.fft.fft(output_block, norm="ortho") / self.rate

                # Update y-data of plot
                self.view.spectrum_x.set_ydata(np.abs(X))
                self.view.spectrum_y.set_ydata(np.abs(Y))
            else:
                s_count += 1

            # Wave Plot
            if self.view.show_wave and w_count > 0:
                w_count = 0
                self.view.wave_x.set_ydata(input_tuple)
                self.view.wave_y.set_ydata(output_block)
            else:
                w_count += 1

            output_block = np.clip(output_block, -32768, 32767)

            binary_data = struct.pack('h' * self.block_len, *output_block)
            self.stream.write(binary_data)

            if hasattr(self, 'output_wf') and self.output_wf:
                self.output_wf.writeframes(binary_data)

            self.view.update()

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


#app = App()
#
app = App()
app.start()