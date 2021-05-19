import os
import platform
import shutil
from pathlib import Path
from typing import Tuple, Union
from uuid import uuid4

import pytest

TEST_DIR = Path(os.path.dirname(os.path.abspath(__file__)))


# every function need to sleep for a while to wait for the reload to complete
def pytest_addoption(parser):
    parser.addoption("--wait", action="store", default=0.3, )


def pytest_generate_tests(metafunc):
    option_value = float(metafunc.config.option.wait)
    if 'wait' in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("wait", [option_value])


def read_replace_write(file: Union[str, Path], replace: Tuple):
    with open(file, 'r') as f:
        raw = f.read()

    with open(file, 'w') as f:
        text = raw.replace(*replace)
        f.write(text)


# create a unique directory for each test
# we can't reload the same pkg name
@pytest.fixture
def pkg_name():
    return f'my_pkg_{str(uuid4())}'


def copy_pkg(pkg_name):
    pkg = TEST_DIR.parent / 'my_pkg'
    dest = TEST_DIR / pkg_name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(pkg, dest)


@pytest.fixture(scope='function', autouse=True)
def create_package(pkg_name):
    copy_pkg(pkg_name)
    pkg_dir = TEST_DIR / pkg_name
    yield
    try:
        shutil.rmtree(pkg_dir)
    # When test in NSF file system this is a workaround
    except Exception as e:
        pass
    try:
        if platform.system() in ['Linux', 'Darwin']:
            os.system(f"rm -rf {pkg_dir.absolute()}")
        else:
            os.system(f"rmdir \\Q \\S {pkg_dir.absolute()}")
    except Exception as e:
        pass


@pytest.fixture(scope='function')
def package(pkg_name):
    pkg_dir = TEST_DIR / pkg_name
    pkg_init: Path = pkg_dir / '__init__.py'
    pkg_file_module: Path = pkg_dir / 'file_module.py'
    pkg_sub_module_init: Path = pkg_dir / 'sub_module' / '__init__.py'
    pkg_subsub_module_init: Path = pkg_dir / 'sub_module' / 'subsub_module' / '__init__.py'

    class Package:
        pkg_name = pkg_name
        pkg_init: Path = pkg_dir / '__init__.py'
        pkg_file_module: Path = pkg_dir / 'file_module.py'
        pkg_sub_module_init: Path = pkg_dir / 'sub_module' / '__init__.py'
        pkg_subsub_module_init: Path = pkg_dir / 'sub_module' / 'subsub_module' / '__init__.py'

        @staticmethod
        def raise_syntax_error():
            read_replace_write(pkg_init, ("return", "return_"))

        @staticmethod
        def modify_module_func():
            read_replace_write(pkg_init, ("Hi from func", "Hello from func"))
            # with open(pkg_init, 'r') as f:
            #     print(f.read())

        @staticmethod
        def modify_module_decorated_func():
            read_replace_write(pkg_init, ("return 100", "return 10"))

        @staticmethod
        def modify_module_class():
            read_replace_write(pkg_init, ("v = 1", "v = 2"))

        @staticmethod
        def modify_file_module_func():
            read_replace_write(pkg_file_module, ("Hi from file_func", "Hello from file_func"))

        @staticmethod
        def modify_sub_module_func():
            read_replace_write(pkg_sub_module_init, ("Hi from sub_func", "Hello from sub_func"))

        @staticmethod
        def modify_sub_module_decorated_func():
            read_replace_write(pkg_sub_module_init, ("return 100", "return 10"))

        @staticmethod
        def modify_sub_module_class():
            read_replace_write(pkg_sub_module_init, ("v = 1", "v = 2"))

        @staticmethod
        def modify_subsubmodule():
            read_replace_write(pkg_subsub_module_init, ("x = 1", "x = 2"))

    return Package()
