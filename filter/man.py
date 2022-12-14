import numpy as np
from filter.function import Function


class ManFilter(Function):
    def __init__(self, rate, block_len):
        super().__init__(rate, block_len)

    def activate(self, view, input_tuple):

        gain = view.man_gain.get() / 100
        alpha = view.man_freq.get()

        shift = int(alpha / self.rate * len(input_tuple))
        signal_fft = np.fft.rfft(input_tuple)
        signal_fft_rolled = np.roll(signal_fft, shift)
        if alpha >= 0:
            signal_fft_rolled[0:shift] = 0
        else:
            signal_len = len(signal_fft_rolled)
            signal_fft_rolled[signal_len + shift:] = 0.
        signal_pitched = (gain * np.fft.irfft(signal_fft_rolled)).astype(int)

        return signal_pitched - input_tuple
