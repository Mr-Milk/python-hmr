# Python Hot Module Reload

![Test status](https://img.shields.io/github/workflow/status/Mr-Milk/python-hmr/Test?label=Test&logo=github&style=flat-square)
![codecov](https://img.shields.io/codecov/c/github/Mr-Milk/python-hmr?style=flat-square)
![pypi](https://img.shields.io/pypi/v/python-hmr?logoColor=white&style=flat-square)
![license-mit](https://img.shields.io/github/license/Mr-Milk/python-hmr?color=blue&style=flat-square)

Automatic reload your project when files are modified.

No need to modify your source code.

![reload](img/reload_func.gif)

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

If your application contains submodule that handle state, 
you can exclude it from reloading.

`excluded` only works with module type

> Make sure you know what you are doing. 
> This could lead to unexpected behavior and unreproducible bugs.
```python
import my_pkg

from hmr import Reloader
my_pkg = Reloader(my_pkg, excluded=['my_pkg.state'])
```

### Function/Class reload

No difference to reloading module

```python
from my_pkg import func, Class

from hmr import Reloader
func = Reloader(func)
Class = Reloader(Class)
```

### @Decorated Function reload

Use [functools.wraps](https://docs.python.org/3/library/functools.html#functools.wraps) to preserve 
signature of your function, or the function information will be replaced by the decorator itself.

## Acknowledgement

Inspired from the following package.

- [auto-reloader](https://github.com/moisutsu/auto-reloader)
- [reloadr](https://github.com/hoh/reloadr)