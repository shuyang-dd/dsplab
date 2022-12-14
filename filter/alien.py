import math
from filter.function import Function


class AlienFilter(Function):
    def __init__(self, rate, block_len):
        super().__init__(rate, block_len)

        # alien parameters
        self.f0 = 10
        self.W = 0.2

        self.buffer_len = 1024
        self.buffer = self.buffer_len * [0]

        self.read_index = 0
        self.write_index = int(0.5 * self.buffer_len)

        self.om = 2 * math.pi * self.f0 / self.rate
        self.theta = 0

    def activate(self, view, input_tuple):

        self.f0 = view.alien_f0.get()
        self.W = view.alien_w.get()
        self.om = 2 * math.pi * self.f0 / self.rate

        diff_block = [0] * self.block_len

        for n in range(0, self.block_len):
            x0 = input_tuple[n]

            read_index_prev = int(math.floor(self.read_index))
            frac = self.read_index - read_index_prev
            read_index_next = read_index_prev + 1
            if read_index_next == self.buffer_len:
                read_index_next = 0

            diff_block[n] = int(
                (1-frac) * self.buffer[read_index_prev] + frac * self.buffer[read_index_next]) - x0

            self.buffer[self.write_index] = x0

            self.theta += self.om
            self.read_index = self.read_index + \
                1 + self.W * math.sin(self.theta)

            while self.theta > math.pi:
                self.theta = self.theta - 2*math.pi

            if self.read_index >= self.buffer_len:
                self.read_index = self.read_index - self.buffer_len

            self.write_index = self.write_index + 1
            if self.write_index == self.buffer_len:
                self.write_index = 0

        return diff_block
