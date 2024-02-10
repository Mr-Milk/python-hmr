<p align="center">
    <picture align="center">
    <img src="https://raw.githubusercontent.com/Mr-Milk/python-hmr/main/assets/logo.svg" 
    alt="python-hmr logo"height="50"/>
    </picture>
</p>
<p align="center">
  <i>Better debugging experience with HMR</i>
</p>

# Python Hot Module Reload

![Test status](https://img.shields.io/github/actions/workflow/status/Mr-Milk/python-hmr/test.yaml?label=Test&logo=github&style=flat-square)
![pypi](https://img.shields.io/pypi/v/python-hmr?logoColor=white&style=flat-square)
![license-mit](https://img.shields.io/github/license/Mr-Milk/python-hmr?color=blue&style=flat-square)
![Endpoint Badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Mr-Milk/python-hmr/main/assets/badge/logo.json&style=social)


Automatic reload your project when files are modified.

No need to modify your source code. Works at any environment.

![reload](https://github.com/Mr-Milk/python-hmr/blob/main/assets/showcase/reload_demo.gif?raw=true)

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

> ![Caution]
> From v0.3.0, there is only one API `hmr.reload`.

Import your dev packages as usual. And add 2 lines 
for automatically reload.

```python
import dev

import hmr
dev = hmr.reload(dev)
```

If you have multiple modules to reload, you can do it like this.

```python
from dev import run1, run2

import hmr
run1, run2 = hmr.reload(run1, run2)
```

Now you are ready to go! Try to modify the `run1` or `run2`
and see the magic happens.


## Detailed Usage


### Function/Class instance

When you try to add HMR for a function or class, remember to
pass the name of the function or class instance without parenthesis.

```python
from dev import Runner

import hmr
Runner = hmr.reload(Runner)

a = Runner()
b = Runner()
```

> ![Important]
> Here, when both `a` and `b` will be updated after reloading. This maybe helpful
> if you have a expansive state store within the class instance.
>
> However, it's suggested to reinitialize the class instance after reloading.


### @Decorated Function

Use [functools.wraps](https://docs.python.org/3/library/functools.html#functools.wraps) to preserve 
signature of your function, or the function information will be replaced by the decorator itself.

```python
import functools

def work(f):
    @functools.wraps(f)
    def args(*arg, **kwargs):
        return f(*arg, **kwargs)

    return args
```

### Stateful application

If your application is stateful, you can exclude the state from being reloaded.
For simplicity, you can group all your state variable into the same `.py` file like `state.py` 
and exclude that from being reloaded.

> Make sure you know what you are doing. 
> This could lead to unexpected behavior and unreproducible bugs.

```python
import dev

import hmr
dev = hmr.reload(dev, exclude=["dev.state"])
```

In this way `dev/state.py` will not be reloaded, the state will persist.

This also apply when reloading a function or class.

```python
from dev import run

import hmr
run = hmr.reload(run, exclude=["dev.state"])
```


## Acknowledgement

Inspired from the following package.

- [auto-reloader](https://github.com/moisutsu/auto-reloader)
- [reloadr](https://github.com/hoh/reloadr)