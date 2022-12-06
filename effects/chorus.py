from effects.effect import Effect
import math

class ChorusEffect(Effect):
    def __init__(self, rate, block_len):
        super().__init__(rate, block_len)

        self.buffer_len =  1024          # Set buffer length.
        self.buffer = self.buffer_len * [0]   # list of zeros
        
        self.kr = 0  # read index
        self.kw = int(0.5 * self.buffer_len)  # write index (initialize to middle of buffer)

        self.f0 = 1
        
    def apply(self, view, input_tuple):

        self.W = view.chorus_w.get()
        self.G = view.chorus_gain.get() / 100

        diff_block = [0] * self.block_len

        for n in range(0, self.block_len):

            x0 = input_tuple[n]

            # Get previous and next buffer values (since kr is fractional)
            kr_prev = int(math.floor(self.kr))
            frac = self.kr - kr_prev  # 0 <= frac < 1
            kr_next = kr_prev + 1
            if kr_next == self.buffer_len:
                kr_next = 0
            
            # Chorus effect
            # diff_block[n] = x0 + int(self.G * ((1 - frac) * self.buffer[kr_prev] + frac * self.buffer[kr_next]))
            diff_block[n] = int(self.G * ((1 - frac) * self.buffer[kr_prev] + frac * self.buffer[kr_next]))

            # Update buffer
            self.buffer[self.kw] = x0

            self.kr = self.kr + 1 + self.W * math.sin(2 * math.pi * self.f0 * n / self.rate)

            # Ensure that 0 <= kr < buffer_len
            if self.kr >= self.buffer_len:
                # End of buffer. Circle back to front.
                self.kr = self.kr - self.buffer_len

            # Increment write index    
            self.kw = self.kw + 1
            if self.kw == self.buffer_len:
                # End of buffer. Circle back to front.
                self.kw = 0

        return diff_block