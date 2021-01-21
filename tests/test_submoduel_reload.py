from time import sleep

import pytest_check as check

# import X.Y
from hmr import Reloader


# import X.Y as A
def test_submodule(package, wait):
    import my_pkg.sub_module as sub
    sub = Reloader(sub)

    package.reset()
    check.equal(sub.sub_func(), "Hi from sub_func")

    package.modify_sub_module_func()
    sleep(wait)
    check.equal(sub.sub_func(), "Hello from sub_func")
    package.reset()

    sub.stop()
