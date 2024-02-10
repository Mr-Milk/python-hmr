from .file_module import file_func
from .sub_module import sub_func
from .wrap import work_wrap


def func():
    return "Hi from func"


@work_wrap
@work_wrap
def decorated_func():
    return 100


class Class:
    v = 1


var = 1


class Complicate:
    """Complicate class for testing purposes."""

    def __init__(self):
        self.x = 12

    # def __repr__(self):
    #     return f"Complicate(x={self.x})"

    def __add__(self, other):
        return self.x + other.x

    def __call__(self, *args, **kwargs):
        return self.add(*args)

    def add(self, a, b):
        return a + b + self.x
