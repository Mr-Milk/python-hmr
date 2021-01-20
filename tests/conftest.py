import pytest
from pathlib import Path
import shutil
from time import sleep


@pytest.fixture(scope='session', autouse=True)
def create_package():
    project_root = Path().cwd()
    pkg = project_root / 'my_pkg'
    shutil.copytree(pkg, project_root / 'tests' / 'my_pkg')
    yield
    shutil.rmtree(project_root / 'tests' / 'my_pkg')


def read_raw(file):
    with open(file, 'r') as f:
        raw = f.read()
    return raw


def write_raw(file, text):
    with open(file, 'w+') as f:
        f.write(text)


# every function need to sleep for a while to wait for the reload to complete
class Package:
    wait = 0.5

    def __init__(self):
        self.pkg = Path.cwd() / 'tests' / 'my_pkg'
        self.code_dir = dict(
            pkg_init=self.pkg / '__init__.py',
            pkg_file_module=self.pkg / 'file_module.py',
            pkg_sub_module_init=self.pkg / 'sub_module' / '__init__.py',
            pkg_subsub_module_init=self.pkg / 'sub_module' / 'subsub_module' / '__init__.py'
        )
        self.pkg_init = read_raw(self.code_dir['pkg_init'])
        self.pkg_file_module = read_raw(self.code_dir['pkg_file_module'])
        self.pkg_sub_module_init = read_raw(self.code_dir['pkg_sub_module_init'])
        self.pkg_subsub_module_init = read_raw(self.code_dir['pkg_subsub_module_init'])

    def raise_syntax_error(self):
        with open(self.code_dir['pkg_init'], 'w') as f:
            f.write(self.pkg_init.replace(f"return", "return_"))
        sleep(self.wait)

    def modify_module_func(self):
        with open(self.code_dir['pkg_init'], 'w') as f:
            f.write(self.pkg_init.replace("Hi from func", "Hello from func"))
        sleep(self.wait)

    def modify_module_decorated_func(self):
        with open(self.code_dir['pkg_init'], 'w') as f:
            f.write(self.pkg_init.replace("return 100", "return 10"))
        sleep(self.wait)

    def modify_module_class(self):
        with open(self.code_dir['pkg_init'], 'w') as f:
            f.write(self.pkg_init.replace("v = 1", "v = 2"))
        sleep(self.wait)

    def modify_file_module_func(self):
        with open(self.code_dir['pkg_file_module'], 'w') as f:
            f.write(self.pkg_file_module.replace("Hi from file_func", "Hello from file_func"))
        sleep(self.wait)

    def modify_sub_module_func(self):
        with open(self.code_dir['pkg_sub_module_init'], 'w') as f:
            f.write(self.pkg_sub_module_init.replace("Hi from sub_func", "Hello from sub_func"))
        sleep(self.wait)

    def modify_sub_module_decorated_func(self):
        with open(self.code_dir['pkg_sub_module_init'], 'w') as f:
            f.write(self.pkg_sub_module_init.replace("return 100", "return 10"))
        sleep(self.wait)

    def modify_sub_module_class(self):
        with open(self.code_dir['pkg_sub_module_init'], 'w') as f:
            f.write(self.pkg_sub_module_init.replace("v = 1", "v = 2"))
        sleep(self.wait)

    def modify_subsubmodule(self):
        with open(self.code_dir['pkg_subsub_module_init'], 'w') as f:
            f.write(self.pkg_subsub_module_init.replace("x = 1", "x = 2"))
        sleep(self.wait)

    def reset(self):
        write_raw(self.code_dir['pkg_init'], self.pkg_init)
        write_raw(self.code_dir['pkg_file_module'], self.pkg_file_module)
        write_raw(self.code_dir['pkg_sub_module_init'], self.pkg_sub_module_init)
        write_raw(self.code_dir['pkg_subsub_module_init'], self.pkg_subsub_module_init)
        sleep(self.wait)


@pytest.fixture(scope='module')
def package(create_package):
    return Package()
