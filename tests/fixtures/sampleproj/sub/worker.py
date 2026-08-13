import os.path

import sampleproj.helpers as h
from ..models import Engine


def work():
    eng = Engine()
    h.util_b()
    return os.path.join("x", str(eng))
