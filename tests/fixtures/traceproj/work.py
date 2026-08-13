def add(a: int, b: int) -> int:
    return a + b


def helper(n):
    return n * 2


def chain(n):
    return helper(n)


class Repo:
    def __init__(self):
        self.count = 0

    def bump(self, k):
        self.count += k
        return self.count


def many(x):
    return x


def outer():
    def inner(v):
        return v

    return inner(7)


def fact(n):
    if n <= 1:
        return 1
    return n * fact(n - 1)


def uses_lambda():
    f = lambda v: v + 1  # noqa: E731
    return f(1)


def main():
    add(1, 2)
    chain(3)
    repo = Repo()
    for i in range(8):
        many(i)
    repo.bump(5)
    outer()
    fact(4)
    return "done"
