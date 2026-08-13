import os.path

import sampleproj.helpers as h
from .helpers import fact, util_a
from .models import Engine


def main():
    util_a()
    util_a()
    fact(5)
    h.util_b()
    engine = Engine()
    engine.start()
    print(os.path.join("a", "b"))
    return engine


if __name__ == "__main__":
    main()
