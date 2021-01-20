import functools


def wrap(f):
    def args(*arg, **kwargs):
        return f(*arg, **kwargs)

    return args


def work_wrap(f):
    @functools.wraps(f)
    def args(*arg, **kwargs):
        return f(*arg, **kwargs)

    return args
