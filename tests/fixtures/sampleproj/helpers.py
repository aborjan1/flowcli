def util_a():
    return util_b()


def util_b():
    return 2


def fact(n):
    if n <= 1:
        return 1
    return n * fact(n - 1)


def ping(n):
    if n:
        return pong(n - 1)
    return 0


def pong(n):
    return ping(n)


def outer():
    def inner():
        return util_b()

    return inner()
