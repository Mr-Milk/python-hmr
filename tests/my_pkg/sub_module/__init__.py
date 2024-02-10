from tests.my_pkg.wrap import wrap


def sub_func():
    return "Hi from sub_func"


@wrap
@wrap
def decorated_sub_func():
    return 100


class SubClass:
    v = 1
