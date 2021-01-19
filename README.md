# Python Hot Module Reload

Automatic reload your project when files are modified.

No need to modify your source code.

## Usage

Just import your developing package

Supported syntax:

✅ ```import X```

✅ ```import X as Y```

✅ ```from X import Y```

Supported Types:

✅ `Module`

✅ `Function`

✅ `Class`

### Module reload

```shell
from hmr import Reloader

import my_pkg
my_pkg = Reloader(my_pkg)
```

If your application contains submodule that handle state, make sure you know 
what you are doing. This could lead to unexpected behavior and unreproducible bugs.
```shell
from reload import Reloader

import my_pkg
my_pkg = Reloader(my_pkg, excluded=['my_pkg.state'])
```

### Function/Class reload

```shell
from hmr import Reloader

from my_pkg import func, Class
func = Reloader(func)
Class = Reloader(Class)
```

## Installation

```shell
pip install python-hmr
```

## Acknowledgement

This is a package develop for my own need, and inspired from the following package.

- [auto-reloader](https://github.com/moisutsu/auto-reloader)
- [reloadr](https://github.com/hoh/reloadr)