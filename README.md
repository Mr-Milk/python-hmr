<img src="https://raw.githubusercontent.com/Mr-Milk/python-hmr/d642a1054d5502a020f107bebecba41abeb4c7ea/img/logo.svg" alt="python-hmr logo" align="left" height="50" />

# Python Hot Module Reload

![Test status](https://img.shields.io/github/actions/workflow/status/Mr-Milk/python-hmr/test.yaml?label=Test&logo=github&style=flat-square)
![codecov](https://img.shields.io/codecov/c/github/Mr-Milk/python-hmr?style=flat-square)
![pypi](https://img.shields.io/pypi/v/python-hmr?logoColor=white&style=flat-square)
![license-mit](https://img.shields.io/github/license/Mr-Milk/python-hmr?color=blue&style=flat-square)

Automatic reload your project when files are modified.

No need to modify your source code. Works at any environment.

![reload](https://github.com/Mr-Milk/python-hmr/blob/main/img/reload_func.gif?raw=true)

Supported Syntax:

- ✅ ```import X```
- ✅ ```from X import Y```

Supported Types:

- ✅ `Module`
- ✅ `Function`
- ✅ `Class`

## Installation

```shell
pip install python-hmr
```

## Quick Start

Import your dev package as usual.

```python
import my_pkg
```

Add 2 lines to automatically reload your source code.


```python
import my_pkg

import hmr
my_pkg = hmr.reload(my_pkg)
```

Now you are ready to go!

## Usage Manual

### Module/Submodule reload

```python
import my_pkg.sub_module as sub

import hmr
sub = hmr.reload(sub)
```

### Function/Class reload

No difference to reloading module

```python
from my_pkg import func, Class

import hmr
func = hmr.reload(func)
Class = hmr.reload(Class)
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

If your application is not stateless, it's suggested that you 
group all your state variable into the same `.py` file like `state.py` 
and exclude that from being reloaded.

> Make sure you know what you are doing. 
> This could lead to unexpected behavior and unreproducible bugs.

```python
import my_pkg

import hmr
my_pkg = hmr.reload(my_pkg, excluded=["my_pkg.state"])
```

The `my_pkg/state.py` will not be reloaded, the state will persist.

The same apply when reloading a function or class.

```python
from my_pkg import func

import hmr
func = hmr.reload(func, excluded=["my_pkg.state"])
```


## Acknowledgement

Inspired from the following package.

- [auto-reloader](https://github.com/moisutsu/auto-reloader)
- [reloadr](https://github.com/hoh/reloadr)