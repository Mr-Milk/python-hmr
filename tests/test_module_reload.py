import pytest
import pytest_check as check
import inspect
from time import sleep

from hmr import Reloader


# import X

def test_module(package, wait):
    import my_pkg
    my_pkg = Reloader(my_pkg, excluded=['my_pkg.sub_module'])
    check.equal(my_pkg.func(), "Hi from func")
    package.modify_module_func()
    sleep(wait)
    check.equal(my_pkg.func(), "Hello from func")
    package.reset()


@pytest.mark.xfail
def test_syntax_error(package, wait):
    import my_pkg
    my_pkg = Reloader(my_pkg)
    my_pkg.reload()
    check.equal(my_pkg.func(), "Hi from func")

    package.raise_syntax_error()
    my_pkg.reload()
    sleep(wait)
    check.equal(my_pkg.func(), "Hello from func")
    package.reset()

