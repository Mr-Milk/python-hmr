import pytest
import pytest_check as check
from hmr import Reloader


# from X import func
def test_func(package):
    from my_pkg import func
    func = Reloader(func)

    package.reset()
    func.reload()
    check.equal(func(), "Hi from func")

    package.modify_module_func()
    func.reload()
    check.equal(func(), "Hello from func")

    func.stop()


# from X import func as f
def test_ref_func(package):
    from my_pkg import func as f
    f = Reloader(f)

    package.reset()
    f.reload()
    check.equal(f(), "Hi from func")

    package.modify_module_func()
    f.reload()
    check.equal(f(), "Hello from func")

    f.stop()


# from X.Y import func
def test_sub_func(package):
    from my_pkg.sub_module import sub_func
    sub_func = Reloader(sub_func)

    package.reset()
    sub_func.reload()
    check.equal(sub_func(), "Hi from sub_func")

    package.modify_sub_module_func()
    sub_func.reload()
    check.equal(sub_func(), "Hello from sub_func")

    sub_func.stop()


# from X import class
def test_class(package):
    from my_pkg import Class
    Class = Reloader(Class)

    package.reset()
    Class.reload()
    check.equal(Class().v, 1)

    package.modify_module_class()
    Class.reload()
    check.equal(Class().v, 2)

    Class.stop()


# from X import class as c
def test_ref_class(package):
    from my_pkg import Class as c
    c = Reloader(c)

    package.reset()
    c.reload()
    check.equal(c.v, 1)

    package.modify_module_class()
    c.reload()
    check.equal(c.v, 2)

    c.stop()


# from X.Y import class
def test_sub_class(package):
    from my_pkg.sub_module import SubClass
    SubClass = Reloader(SubClass)

    package.reset()
    SubClass.reload()
    check.equal(SubClass().v, 1)

    package.modify_sub_module_class()
    SubClass.reload()
    check.equal(SubClass().v, 2)

    SubClass.stop()


# from X import var
@pytest.mark.xfail
def test_var():
    from my_pkg import var
    var = Reloader(var)


# test ref object reload
def test_func_ref_reload(package):
    from my_pkg import func
    func = Reloader(func)
    ref_f = func

    package.reset()
    func.reload()
    check.equal(func(), "Hi from func")
    check.equal(ref_f(), "Hi from func")

    package.modify_module_func()
    func.reload()
    check.equal(func(), "Hello from func")
    check.equal(ref_f(), "Hello from func")

    func.stop()


def test_class_ref_reload(package):
    from my_pkg import Class
    Class = Reloader(Class)
    a = Class()
    b = Class()

    package.reset()
    Class.reload()
    check.equal(a.v, 1)
    check.equal(b.v, 1)

    package.modify_module_class()
    Class.reload()
    check.equal(a.v, 2)
    check.equal(b.v, 2)

    Class.stop()


# test decorated function
def test_decoreated_function_with_signature(package):
    from my_pkg import decorated_func
    decorated_func = Reloader(decorated_func)

    package.reset()
    decorated_func.reload()
    check.equal(decorated_func(), 100)

    package.modify_module_decorated_func()
    decorated_func.reload()
    check.equal(decorated_func(), 10)

    decorated_func.stop()


@pytest.mark.xfail
def test_decoreated_function_no_signature(package):
    from my_pkg.sub_module import decorated_sub_func as dsf
    dsf = Reloader(dsf)

    package.reset()
    dsf.reload()
    check.equal(dsf(), 100)
    package.modify_sub_module_decorated_func()
    dsf.reload()
    check.equal(dsf(), 10)

    dsf.stop()
