import tkinter as Tk
from matplotlib import pyplot as plt
import numpy as np
from tkinter import filedialog as fd
from tkinter import messagebox
from Transcripter import Transcripter
from tkinter import ttk
import sv_ttk


class View(Tk.Tk):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.Transcripter = Transcripter()

        self.running = True
        self.show_wave = False
        self.show_spectrum = False
        self.show_transcript = False

        sv_ttk.set_theme('dark')

        # initial variable
        self.status = Tk.StringVar(value='Stopped')
        self.file_path = Tk.StringVar(value='')
        self.save_file = Tk.BooleanVar()
        self.save_name = Tk.StringVar(value='recording.wav')

        # transcript
        self.message = ttk.Label(
            self, text="Live caption: "+self.Transcripter.text, wraplength=500)
        self.message.grid(row=6, column=0, sticky='W')
        self.update_text()

        # input and output
        self.io_frame = ttk.LabelFrame(
            self, text="Input and Output")
        self.io_frame.grid(row=0, column=0, columnspan=2)

        # input and output
        self.input_mode = Tk.IntVar(value=1)
        self.mic_btn = ttk.Radiobutton(
            self.io_frame,
            text="Microphone",
            variable=self.input_mode,
            command=self.on_input_change,
            value=1,
        )
        self.mic_btn.grid(row=0, column=0, sticky='W', padx=4)

        self.file_btn = ttk.Radiobutton(
            self.io_frame,
            text="Wave file",
            variable=self.input_mode,
            command=self.on_input_change,
            value=2,
        )
        self.file_btn.grid(row=0, column=1, sticky='W', padx=5)

        ttk.Label(self.io_frame, text='Status:').grid(
            row=0, column=2, sticky='E')
        self.status_label = ttk.Label(
            self.io_frame,
            textvariable=self.status,
            width=12,
            relief=Tk.SUNKEN,
        )
        self.status_label.grid(row=0, column=3, padx=10, sticky='E')

        self.open_btn = ttk.Button(
            self.io_frame,
            text='Open file',
            command=self.handle_open_file
        )
        self.open_btn.grid(row=1, column=0, pady=5)
        self.open_btn.configure(state='disable')

        io_label = ttk.Frame(self.io_frame)
        io_label.grid(row=1, column=1, columnspan=3)
        ttk.Label(
            io_label,
            textvariable=self.file_path,
            width=54,
            relief=Tk.SUNKEN,
            anchor='w'
        ).pack()

        self.save_btn = ttk.Checkbutton(
            self.io_frame,
            text="Save file",
            variable=self.save_file,
            onvalue=True,
            offvalue=False
        )
        self.save_btn.grid(row=2, column=0)

        self.save_entry = ttk.Entry(
            self.io_frame,
            textvariable=self.save_name,
            width=54,
            # bd=1
        )
        self.save_entry.grid(row=2, column=1, columnspan=3)

        # advanced options
        self.button_frame = ttk.LabelFrame(self, text="Graph")
        self.button_frame.grid(row=2, column=0, columnspan=2)

        # Button - Wave Graph
        ttk.Button(
            self.button_frame,
            text='Wave Graph',
            command=self.open_wave
        ).grid(row=0, column=0)

        # Button - Spectrum Graph
        ttk.Button(
            self.button_frame,
            text='Spectrum Graph',
            command=self.open_spectrum
        ).grid(row=0, column=1)

        # general button
        self.general_btn = ttk.LabelFrame(self)
        self.general_btn.grid(row=3, column=0, columnspan=2)

        # start
        ttk.Button(
            self.general_btn,
            text='Start',
            command=self.start_play
        ).grid(row=0, column=0, pady=8)

        # stop
        ttk.Button(
            self.general_btn,
            text='Stop',
            command=self.stop_play
        ).grid(row=0, column=1, pady=8)

        # quit
        ttk.Button(
            self.general_btn,
            text='Quit',
            command=self.handle_quit
        ).grid(row=0, column=2)

        # filters
        self.effect_frame = ttk.LabelFrame(self, text="Filter Select & Adjust")
        self.effect_frame.grid(row=1, column=0, columnspan=2)

        # mode select
        self.effect_radio = ttk.Frame(self.effect_frame)
        self.effect_radio.grid(row=0, column=0, sticky='W')

        self.effect_mode = Tk.IntVar(value=0)

        # define availble filter
        self.echo_enable = Tk.BooleanVar()
        self.alien_enable = Tk.BooleanVar()
        self.robot_enable = Tk.BooleanVar()
        self.man_enable = Tk.BooleanVar()
        self.woman_enable = Tk.BooleanVar()

        ttk.Radiobutton(
            self.effect_radio,
            text="Echo",
            variable=self.effect_mode,
            value=0,
            command=self.on_effect_mode_change
        ).grid(row=0, column=0, sticky='W')

        ttk.Radiobutton(
            self.effect_radio,
            text="Alien",
            variable=self.effect_mode,
            value=1,
            command=self.on_effect_mode_change
        ).grid(row=0, column=1, sticky='W')

        ttk.Radiobutton(
            self.effect_radio,
            text="Man",
            variable=self.effect_mode,
            value=2,
            command=self.on_effect_mode_change
        ).grid(row=0, column=2, sticky='W')

        ttk.Radiobutton(
            self.effect_radio,
            text="Woman",
            variable=self.effect_mode,
            value=3,
            command=self.on_effect_mode_change
        ).grid(row=0, column=3, sticky='W')

        ttk.Radiobutton(
            self.effect_radio,
            text="Robot",
            variable=self.effect_mode,
            value=4,
            command=self.on_effect_mode_change
        ).grid(row=0, column=4, sticky='W')

        # echo filter
        self.echo_frame = ttk.Frame(self.effect_frame)
        self.echo_frame.grid(row=1, column=0, sticky='W')

        self.echo_feedback = Tk.DoubleVar(value=70)
        self.echo_delay = Tk.DoubleVar(value=0.1)

        # feedback
        self.slide(self.echo_frame, self.echo_feedback,
                   0, 'Feedback (%)', 0.0, 100.0)

        # delay
        self.slide(self.echo_frame, self.echo_delay,
                   1, 'Delay (s)', 0.01, 0.50)

        # alien
        self.alien_frame = ttk.Frame(self.effect_frame)

        self.alien_f0 = Tk.DoubleVar(value=5)
        self.alien_w = Tk.DoubleVar(value=0.2)

        # freq
        self.slide(self.alien_frame, self.alien_f0,
                   0, 'Freq (Hz)', 1.0, 10.0)

        # oscillation
        self.slide(self.alien_frame, self.alien_w,
                   1, 'Oscillation', 0.2, 1.0)

        # robot
        self.robot_frame = ttk.Frame(self.effect_frame)

        self.robot_gain = Tk.DoubleVar(value=80)
        self.robot_frequency = Tk.DoubleVar(value=200)

        # gain
        self.slide(self.robot_frame, self.robot_gain,
                   0, 'Gain (%)', 0.0, 100.0)

        # freq
        self.slide(self.robot_frame, self.robot_frequency,
                   1, 'Freq (Hz)', 200, 1000)

        # man
        self.man_frame = ttk.Frame(self.effect_frame)

        self.man_gain = Tk.DoubleVar(value=80)
        self.man_freq = Tk.DoubleVar(value=100)

        # gain
        self.slide(self.man_frame, self.man_gain,
                   0, 'Gain (%)', 1.0, 100.0)

        # freq
        self.slide(self.man_frame, self.man_freq,
                   1, 'Freq (Hz)', -800, 100)

        # woman
        self.woman_frame = ttk.Frame(self.effect_frame)

        self.woman_gain = Tk.DoubleVar(value=80)
        self.woman_freq = Tk.DoubleVar(value=0)

        # gain
        self.slide(self.woman_frame, self.woman_gain,
                   0, 'Gain (%)', 1.0, 100.0)

        # freq
        self.slide(self.woman_frame, self.woman_freq,
                   1, 'Freq (Hz)', 0, 1000)

        self.frames = [self.echo_frame, self.alien_frame,
                       self.man_frame, self.woman_frame, self.robot_frame]
        plt.ion()

    def update_text(self):
        self.message.config(text="Live caption: " +
                            self.Transcripter.text)

        self.after(100, self.update_text)

    def handle_quit(self):
        self.running = False

    def is_running(self):
        return self.running

    def on_effect_mode_change(self):
        mode = self.effect_mode.get()
        for i, frame in enumerate(self.frames):
            if i == mode:
                frame.grid(row=1, column=0, sticky='W')
            else:
                frame.grid_remove()

        self.echo_enable.set(False)
        self.alien_enable.set(False)
        self.robot_enable.set(False)
        self.man_enable.set(False)
        self.woman_enable.set(False)
        if mode == 0:
            self.echo_enable.set(True)
        elif mode == 1:
            self.alien_enable.set(True)
        elif mode == 2:
            self.man_enable.set(True)
        elif mode == 3:
            self.woman_enable.set(True)
        elif mode == 4:
            self.robot_enable.set(True)

    def on_input_change(self):
        mode = self.input_mode.get()
        if mode == 1:
            self.open_btn.configure(state='disable')
        if mode == 2:
            self.open_btn.configure(state='normal')

    def handle_open_file(self):
        filepath = fd.askopenfilename(filetypes=(('Wave File', '*.wav'),))
        if filepath:
            self.file_path.set(filepath)
            self.status.set('File Opened')

    def start_play(self):
        mode = self.input_mode.get()
        if mode == 1:
            self.status.set('Recording')
        elif mode == 2:
            if self.file_path.get():
                self.status.set('Playing')
            else:
                messagebox.showerror('Error', 'Please open a wave file')
                return
        self.mic_btn.configure(state='disable')
        self.file_btn.configure(state='disable')
        self.open_btn.configure(state='disable')
        self.save_btn.configure(state='disable')
        self.save_entry.configure(state='disable')
        self.app.change_mode(mode)

    def stop_play(self):
        if self.save_file.get():
            self.status.set('File Saved')
        else:
            self.status.set('Stopped')
        self.mic_btn.configure(state='normal')
        self.file_btn.configure(state='normal')
        self.open_btn.configure(state='normal')
        self.save_btn.configure(state='normal')
        self.save_entry.configure(state='normal')
        self.app.change_mode(0)
        self.app.stop_audio()

    def open_wave(self):
        plt.figure(1)

        plt.xlabel('Time (ms)')

        self.show_wave = True
        self.wave_x, = plt.plot([], [], color='blue', label='Original')
        self.wave_y, = plt.plot([], [], color='red', label='Processed')

        t = [n*1000/float(self.app.rate) for n in range(self.app.block_len)]

        plt.xlim(0, 1000.0 * self.app.block_len /
                 self.app.rate)
        plt.xlabel('Time (msec)')

        plt.ylim(-8000, 8000)

        self.wave_x.set_xdata(t)
        self.wave_y.set_xdata(t)

        self.wave_x.set_ydata(np.zeros(self.app.block_len))
        self.wave_y.set_ydata(np.zeros(self.app.block_len))

        plt.legend()

    def open_spectrum(self):
        plt.figure(2)
        plt.xlim(0, 0.25 * self.app.rate)
        plt.ylim(0, 1)
        plt.xlabel('Frequency (Hz)')

        self.show_spectrum = True
        self.spectrum_x, = plt.plot([], [], color='blue', label='Original')
        self.spectrum_y, = plt.plot([], [], color='red', label='Processed')

        f = self.app.rate / self.app.block_len * \
            np.arange(0, self.app.block_len)

        self.spectrum_x.set_xdata(f)
        self.spectrum_y.set_xdata(f)

        self.spectrum_x.set_ydata(np.zeros(self.app.block_len))
        self.spectrum_y.set_ydata(np.zeros(self.app.block_len))

        plt.legend()

    def slide(self, frame, slider_var, row, title, min_num, max_num):
        ttk.Label(
            frame,
            text=title,
            width=12,
            anchor='e'
        ).grid(row=row, column=0, sticky='E', pady=5)

        ttk.Label(
            frame,
            text=min_num,
            width=3
        ).grid(row=row, column=2)

        ttk.Scale(
            frame,
            orient='horizontal',
            variable=slider_var,
            from_=min_num,
            to=max_num,
            length=120
        ).grid(row=row, column=3)

        ttk.Label(
            frame,
            text=max_num,
            width=4,
        ).grid(row=row, column=4)
