import pytest
import pytest_check as check
from hmr import Reloader
from conftest import read_raw


def reload_func(obj, call_obj, package, modify_func, assert_before, assert_after, **kwargs):
    obj = Reloader(obj, **kwargs)

    package.reset()
    obj.reload()
    check.equal(getattr(obj, call_obj).__call__(), assert_before)

    getattr(package, modify_func).__call__()
    obj.reload()
    check.equal(getattr(obj, call_obj).__call__(), assert_after)

    obj.stop()


def reload_class(obj, call_obj, attr, package, modify_func, assert_before, assert_after, **kwargs):
    obj = Reloader(obj, **kwargs)

    package.reset()
    obj.reload()
    check.equal(getattr(getattr(obj, call_obj).__call__(), attr), assert_before)

    getattr(package, modify_func).__call__()

    print(read_raw(package.code_dir['pkg_sub_module_init']))
    obj.reload()
    check.equal(getattr(getattr(obj, call_obj).__call__(), attr), assert_after)

    obj.stop()


# import X
def test_module(package):
    import my_pkg
    reload_func(my_pkg, 'func', package, 'modify_module_func',
                "Hi from func", "Hello from func", excluded=['my_pkg.sub_module'])


# import X as A
def test_ref_module(package):
    import my_pkg as mp
    reload_func(mp, 'func', package, 'modify_module_func',
                "Hi from func", "Hello from func")


# import X.Y
def test_submodule(package):
    import my_pkg.sub_module
    reload_func(my_pkg.sub_module, 'sub_func', package, 'modify_sub_module_func',
                "Hi from sub_func", "Hello from sub_func",)


# import X.Y as A
def test_ref_submodule(package):
    import my_pkg.sub_module as sub

    reload_class(sub, 'SubClass', 'v', package, 'modify_sub_module_class',
                 1, 2)


# from X import Y
def test_individual_submodule(package):
    from my_pkg import sub_module
    reload_func(sub_module, 'sub_func', package, 'modify_sub_module_func',
                "Hi from sub_func", "Hello from sub_func", )


# from X import Y as A
def test_ref_individual_submodule(package):
    from my_pkg import sub_module as sub
    reload_func(sub, 'sub_func', package, 'modify_sub_module_func',
                "Hi from sub_func", "Hello from sub_func", )


# from X.Y import A
def test_subsubmodule(package):
    from my_pkg.sub_module import subsub_module

    subsub_module = Reloader(subsub_module)

    package.reset()
    subsub_module.reload()
    check.equal(subsub_module.x, 1)

    package.modify_subsubmodule()
    subsub_module.reload()
    check.equal(subsub_module.x, 2)

    subsub_module.stop()


@pytest.mark.xfail
def test_syntax_error(package):
    import my_pkg
    reload_func(my_pkg, 'func', package, 'raise_syntax_error',
                "Hi from func", "Hello from func")

