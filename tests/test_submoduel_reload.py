from time import sleep

import pytest_check as check
from conftest import reload_func, reload_class


# import X.Y
from hmr import Reloader


# import X.Y as A
def test_submodule(package, wait):
    import my_pkg.sub_module as sub
    sub = Reloader(sub)

    package.reset()
    check.equal(sub.SubClass().v, 1)

    package.modify_sub_module_class()
    sleep(wait)
    check.equal(sub.SubClass().v, 2)
    package.reset()

    sub.stop()


# from X import Y
def test_individual_submodule(package, wait):
    from my_pkg import sub_module
    sub_module = Reloader(sub_module)

    package.reset()
    check.equal(sub_module.sub_func(), "Hi from sub_func")

    package.modify_sub_module_func()
    sleep(wait)
    check.equal(sub_module.sub_func(), "Hello from sub_func")
    package.reset()
    sub_module.stop()
