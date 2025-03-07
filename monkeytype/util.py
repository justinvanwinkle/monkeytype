# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
import importlib
import inspect
import re
import types
from functools import cached_property
from typing import Any
from typing import Callable
from typing import Optional

from monkeytype.exceptions import InvalidTypeError
from monkeytype.exceptions import NameLookupError


def get_func_fqname(func: Callable[..., Any]) -> str:
    """Return the fully qualified function name."""
    return func.__module__ + "." + func.__qualname__


def get_func_in_module(module: str, qualname: str) -> Callable[..., Any]:
    """Return the function specified by qualname in module.

    Raises:
        NameLookupError if we can't find the named function
        InvalidTypeError if we the name isn't a function
    """
    func = get_name_in_module(module, qualname)
    func = inspect.unwrap(func)
    if isinstance(func, types.MethodType):
        func = func.__func__
    elif isinstance(func, property):
        if func.fget is not None:
            if (func.fset is None) and (func.fdel is None):
                func = func.fget
            else:
                msg = f"Property {module}.{qualname} has setter or deleter."
                raise InvalidTypeError(msg)
        else:
            msg = f"Property {module}.{qualname} is missing getter"
            raise InvalidTypeError(msg)
    elif isinstance(func, cached_property):
        func = func.func
    elif not isinstance(func, (types.FunctionType, types.BuiltinFunctionType)):
        msg = f"{module}.{qualname} is of type '{type(func)}', not function."
        raise InvalidTypeError(msg)
    return func  # type: ignore[no-any-return]


def get_name_in_module(
    module: str,
    qualname: str,
    attr_getter: Optional[Callable[[Any, str], Any]] = None,
) -> Any:
    """Return the python object specified by qualname in module.

    Raises:
        NameLookupError if the module/qualname cannot be retrieved.
    """
    if attr_getter is None:
        attr_getter = getattr
    try:
        obj = importlib.import_module(module)
    except ModuleNotFoundError as e:
        raise NameLookupError("No module named '%s'" % (module,)) from e
    walked = []
    for part in qualname.split("."):
        walked.append(part)
        try:
            obj = attr_getter(obj, part)
        except AttributeError as e:
            raise NameLookupError(
                "Module '%s' has no attribute '%s'"
                % (module, ".".join(walked))
            ) from e
    return obj


def pascal_case(s: str) -> str:
    return "".join(
        a[0].upper() + a[1:]
        for a in re.split("([^a-zA-Z0-9])", s)
        if a.isalnum()
    )
