import importlib
import sys
from pathlib import Path
from time import sleep

import pytest

from hmr import Reloader

sys.path.insert(0, str(Path(__file__).parent.resolve()))


def check_func(func, modify_func, before, after, wait=0):
    func = Reloader(func)
    assert func() == before

    modify_func()
    sleep(wait)
    assert func.__call__() == after


def check_cls(cls, modify_cls, before, after, wait=0):
    cls = Reloader(cls)
    c = cls()
    assert c.v == before

    modify_cls()
    sleep(wait)
    assert c.v == after


# from X import func
def test_func(package, pkg_name, wait):
    func = importlib.import_module(pkg_name).__getattribute__(
        "func")  # from x import func
    check_func(func, package.modify_module_func, "Hi from func",
               "Hello from func", wait)


# from X.Y import func
def test_sub_func(package, pkg_name, wait):
    sub_func = importlib.import_module(
        f"{pkg_name}.sub_module").__getattribute__("sub_func")
    check_func(sub_func, package.modify_sub_module_func, "Hi from sub_func",
               "Hello from sub_func", wait)


# from X import class
def test_class(package, pkg_name, wait):
    Class = importlib.import_module(pkg_name).__getattribute__("Class")
    check_cls(Class, package.modify_module_class, 1, 2, wait)


# from X.Y import class
def test_sub_class(package, pkg_name, wait):
    SubClass = importlib.import_module(
        f"{pkg_name}.sub_module").__getattribute__("SubClass")
    check_cls(SubClass, package.modify_sub_module_class, 1, 2, wait)


# from X import var
@pytest.mark.xfail
def test_var(pkg_name):
    var = importlib.import_module(pkg_name).__getattribute__("var")
    var = Reloader(var)


# test ref object reload
def test_func_ref_reload(package, pkg_name, wait):
    func = importlib.import_module(pkg_name).__getattribute__("func")
    func = Reloader(func)
    ref_f = func

    assert func() == "Hi from func"
    assert ref_f() == "Hi from func"

    package.modify_module_func()
    sleep(wait)
    assert func() == "Hello from func"
    assert ref_f() == "Hello from func"


def test_class_ref_reload(package, pkg_name, wait):
    Class = importlib.import_module(pkg_name).__getattribute__("Class")
    Class = Reloader(Class)
    assert Class.v == 1
    a = Class()
    b = Class()

    assert a.v == 1
    assert b.v == 1

    package.modify_module_class()
    sleep(wait)
    assert a.v == 2
    assert b.v == 2


# test decorated function
def test_decoreated_function_with_signature(package, pkg_name, wait):
    decorated_func = importlib.import_module(pkg_name).__getattribute__(
        "decorated_func")
    check_func(decorated_func, package.modify_module_decorated_func, 100, 10,
               wait)


@pytest.mark.xfail
def test_decoreated_function_no_signature(package, pkg_name, wait):
    dsf = importlib.import_module(f"{pkg_name}.sub_module").__getattribute__(
        "decorated_sub_func")
    check_func(dsf, package.modify_sub_module_decorated_func, 100, 10, wait)
