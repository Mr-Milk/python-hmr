import importlib
import sys
from pathlib import Path
from time import sleep

import pytest

from hmr import reload

sys.path.insert(0, str(Path(__file__).parent.resolve()))


# import X


def test_module(package, pkg_name, wait):
    my_pkg = importlib.import_module(pkg_name)  # import pkg_name

    my_pkg = reload(my_pkg, exclude=["my_pkg.sub_module"])
    assert my_pkg.func() == "Hi from func"
    package.modify_module_func()
    sleep(wait)
    # check.equal(my_pkg.func(), "Hello from func")
    assert my_pkg.func() == "Hello from func"


# import X.Y as A
def test_submodule(package, pkg_name, wait):
    sub = importlib.import_module(f"{pkg_name}.sub_module")
    sub = reload(sub)

    assert sub.sub_func() == "Hi from sub_func"

    package.modify_sub_module_func()
    sleep(wait)
    assert sub.sub_func() == "Hello from sub_func"


@pytest.mark.xfail
def test_syntax_error(package, pkg_name, wait):
    my_pkg = importlib.import_module(pkg_name)  # import pkg_name
    my_pkg = reload(my_pkg)
    # sleep(wait)
    # check.equal(my_pkg.func(), "Hi from func")
    assert my_pkg.func() == "Hi from func"

    package.raise_syntax_error()
    sleep(wait)
    # check.equal(my_pkg.func(), "Hello from func")
    assert my_pkg.func() == "Hello from func"
