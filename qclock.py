import time

class Clock:
    def __init__(self):
        self.tick()
        self.disabled = False

    def tick(self):
        self.last_tick = time.time()

    @property
    def elapsed(self):
        return time.time() - self.last_tick

    def passed(self, seconds):
        if self.disabled: return False
        return self.elapsed >= seconds

    def set_back(self, seconds):
        self.last_tick -= seconds

    def disable(self):
        self.disabled = True
