from .helpers import util_a


def deco(fn):
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper


@deco
def decorated():
    return util_a()
