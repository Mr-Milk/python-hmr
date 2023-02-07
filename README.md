<img src="https://raw.githubusercontent.com/Mr-Milk/python-hmr/d642a1054d5502a020f107bebecba41abeb4c7ea/img/logo.svg" alt="python-hmr logo" align="left" height="50" />

# Python Hot Module Reload

![Test status](https://img.shields.io/github/workflow/status/Mr-Milk/python-hmr/Test?label=Test&logo=github&style=flat-square)
![codecov](https://img.shields.io/codecov/c/github/Mr-Milk/python-hmr?style=flat-square)
![pypi](https://img.shields.io/pypi/v/python-hmr?logoColor=white&style=flat-square)
![license-mit](https://img.shields.io/github/license/Mr-Milk/python-hmr?color=blue&style=flat-square)

Automatic reload your project when files are modified.

No need to modify your source code.

![reload](https://github.com/Mr-Milk/python-hmr/blob/main/img/reload_func.gif?raw=true)

Supported Syntax:

- ✅ ```import X```
- ✅ ```import X as Y```
- ✅ ```from X import Y```
- ✅ ```from X import Y as A```

Supported Types:

- ✅ `Module`
- ✅ `Function`
- ✅ `Class`

## Installation

```shell
pip install python-hmr
```

## Usage

Just import your developing package and replace it with `Reloader`.

Then you can use it exactly like how you use a module before.

```python
import my_pkg

from hmr import Reloader
my_pkg = Reloader(my_pkg)

my_pkg.func()
# >>> "Hi from func"
```

Or you can manually reload it

```python
my_pkg.reload()
```

To stop the reloading

```python
my_pkg.stop()
```

### Module/Submodule reload

```python
import my_pkg.sub_module as sub

from hmr import Reloader
sub = Reloader(sub)
```

### Function/Class reload

No difference to reloading module

```python
from my_pkg import func, Class

from hmr import Reloader
func = Reloader(func)
Class = Reloader(Class)
```

If your have multiple class instance, they will all be updated. 
Both `a` and `b` will be updated.

```python
a = Class()
b = Class()
```

### @Decorated Function reload

Use [functools.wraps](https://docs.python.org/3/library/functools.html#functools.wraps) to preserve 
signature of your function, or the function information will be replaced by the decorator itself.

### State handling

If your application contains submodule that handle state, 
you can exclude it from reloading. You need to move it to
a new `.py` file like `state.py` and everything from that
file will not be reloaded.

> Make sure you know what you are doing. 
> This could lead to unexpected behavior and unreproducible bugs.

```python
import my_pkg

from hmr import Reloader
my_pkg = Reloader(my_pkg, excluded=["my_pkg.state"])
```

This will exclude the `my_pkg/state.py` from reloading.

Even you only want to reload a submodule or a function, you
still need to provide the `excluded` argument.

```python
import my_pkg.sub_module as sub
from my_pkg import func

from hmr import Reloader
sub = Reloader(sub, excluded=["my_pkg.state"])
func = Reloader(func, excluded=["my_pkg.state"])
```

## Implementation

Current implementation is relied on the `importlib.reload`,
which is not very graceful when handling state. Direct reading of
AST may be a better solution for hot module reload in python,
but it's too complicated, I might try it in the future.

## Acknowledgement

Inspired from the following package.

- [auto-reloader](https://github.com/moisutsu/auto-reloader)
- [reloadr](https://github.com/hoh/reloadr)