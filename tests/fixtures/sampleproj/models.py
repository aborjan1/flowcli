class Base:
    def __init__(self):
        self.state = "ready"

    def start(self):
        return self.step()

    def stop(self):
        return 0


class Engine(Base):
    def step(self):
        return 1

    def start(self):
        return super().start()

    @classmethod
    def build(cls):
        return cls()


class Standalone:
    def __init__(self):
        self.x = 1


def make_engine():
    engine = Engine()
    engine.run()
    return engine


def make_standalone():
    return Standalone()
