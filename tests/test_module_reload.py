import pytest
import pytest_check as check
from hmr import Reloader


# import X
def test_module(package):
    import my_pkg
    my_pkg = Reloader(my_pkg, excluded=['my_pkg.sub_module'])

    package.reset()
    check.equal(my_pkg.func(), "Hi from func")

    package.modify_module_func()
    check.equal(my_pkg.func(), "Hello from func")

    my_pkg.stop()


# import X as A
def test_ref_module(package):
    import my_pkg as mp
    mp = Reloader(mp)

    package.reset()
    check.equal(mp.func(), "Hi from func")

    package.modify_module_func()
    check.equal(mp.func(), "Hello from func")

    mp.stop()


# import X.Y
def test_submodule(package):
    import my_pkg.sub_module
    my_pkg.sub_module = Reloader(my_pkg.sub_module)

    package.reset()
    check.equal(my_pkg.sub_module.sub_func(), "Hi from sub_func")

    package.modify_sub_module_func()
    check.equal(my_pkg.sub_module.sub_func(), "Hello from sub_func")

    my_pkg.sub_module.stop()
    del my_pkg.sub_module


# import X.Y as A
def test_ref_submodule(package):
    import my_pkg.sub_module as sub
    sub = Reloader(sub)

    package.reset()
    check.equal(sub.SubClass().v, 1)

    package.modify_sub_module_class()
    check.equal(sub.SubClass().v, 2)

    sub.stop()


# from X import Y
def test_individual_submodule(package):
    from my_pkg import sub_module
    sub_module = Reloader(sub_module)

    package.reset()
    check.equal(sub_module.sub_func(), "Hi from sub_func")

    package.modify_sub_module_func()
    check.equal(sub_module.sub_func(), "Hello from sub_func")

    sub_module.stop()


# from X import Y as A
def test_ref_individual_submodule(package):
    from my_pkg import sub_module as sub
    sub = Reloader(sub)

    package.reset()
    check.equal(sub.sub_func(), "Hi from sub_func")

    package.modify_sub_module_func()
    check.equal(sub.sub_func(), "Hello from sub_func")

    sub.stop()


# from X.Y import A
def test_subsubmodule(package):
    from my_pkg.sub_module import subsub_module
    subsub_module = Reloader(subsub_module)

    package.reset()
    check.equal(subsub_module.x, 1)

    package.modify_subsubmodule()
    check.equal(subsub_module.x, 2)

    subsub_module.stop()


@pytest.mark.xfail
def test_syntax_error(package):
    import my_pkg
    my_pkg = Reloader(my_pkg)

    package.reset()
    check.equal(my_pkg.func(), "Hi from func")

    package.raise_syntax_error()
    check.equal(my_pkg.func(), "Hello from func")

    my_pkg.stop()
    package.reset()
