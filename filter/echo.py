from filter.function import Function


class EchoFilter(Function):
    def __init__(self, rate, block_len):
        super().__init__(rate, block_len)
        self.delay_update(0.1)

    def activate(self, view, input_tuple):

        gain = view.echo_feedback.get() / 100
        delay = view.echo_delay.get()

        if self.delay_sec != delay:
            self.delay_update(delay)

        diff_block = [0] * self.block_len

        for n in range(0, self.block_len):

            x0 = input_tuple[n]

            y0 = x0 + gain * self.buffer[self.pointer]

            diff_block[n] = self.clip16(y0) - x0

            self.buffer[self.pointer] = x0

            self.pointer = self.pointer + 1
            if self.pointer >= self.buffer_len:
                self.pointer = 0

        return diff_block

    def delay_update(self, delay):
        self.delay_sec = delay
        self.buffer_len = int(self.rate * self.delay_sec)
        self.buffer = self.buffer_len * [0]
        self.pointer = 0
