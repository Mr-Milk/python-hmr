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
