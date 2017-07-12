#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import update_wrapper


def disable(func):
    """
    Disable a decorator by re-assigning the decorator's name
    to this function. For example, to turn off memoization:

    >>> memo = disable

    """
    return func


def decorator(func):
    """
    Decorate a decorator so that it inherits the docstrings
    and stuff from the function it's decorating.
    """
    def inner(*args, **kwargs):
        return func(*args, **kwargs)

    update_wrapper(inner, func)
    return inner


@decorator
def countcalls(func):
    """Decorator that counts calls made to the function decorated."""
    def inner_calls(*args, **kwargs):
        inner_calls.calls += 1
        return func(*args, **kwargs)
    inner_calls.calls = 0
    return inner_calls


@decorator
def memo(func):
    """
    Memoize a function so that it caches all return values for
    faster future lookups.
    """
    cache = {}

    def inner(*args, **kwargs):
        kw_tuple = tuple((k, v) for k, v in kwargs.items())
        result = cache.get((args, kw_tuple))
        if not result:
            result = func(*args, **kwargs)
            cache[(args, kw_tuple)] = result
        return result

    inner.func_dict = func.func_dict
    return inner


@decorator
def n_ary(func):
    """
    Given binary function f(x, y), return an n_ary function such
    that f(x, y, z) = f(x, f(y,z)), etc. Also allow f(x) = x.
    """
    def inner(first, *args):
        return func(first, inner(*args)) if args else first

    return inner


def trace(indent):
    """Trace calls made to function decorated.

        @trace("____")
        def fib(n):
            ....

        >>> fib(3)
         --> fib(3)
        ____ --> fib(2)
        ________ --> fib(1)
        ________ <-- fib(1) == 1
        ________ --> fib(0)
        ________ <-- fib(0) == 1
        ____ <-- fib(2) == 2
        ____ --> fib(1)
        ____ <-- fib(1) == 1
         <-- fib(3) == 3

    """
    def inner(func):
        def wrapper(*args, **kwargs):
            args_to_print = [str(a) for a in args]
            kwargs_to_print = ['{}={}'.format(k, v) for k, v in kwargs.items()]
            params_to_print = ','.join(args_to_print + kwargs_to_print)

            print('{indent} --> {func_name}({params})'.format(
                indent=wrapper.indent, func_name=func.__name__,
                params=params_to_print))

            wrapper.indent += indent
            result = func(*args, **kwargs)

            wrapper.indent = wrapper.indent.replace(indent, '', 1)

            print('{indent} <-- {func_name}({params}) == {result}'.format(
                indent=wrapper.indent, func_name=func.__name__,
                params=params_to_print, result=result))
            return result

        wrapper.indent = ''
        return wrapper

    return inner


@memo
@countcalls
@n_ary
def foo(a, b):
    return a + b


@countcalls
@memo
@n_ary
def bar(a, b):
    return a * b


@countcalls
@trace("####")
@memo
def fib(n):
    return 1 if n <= 1 else fib(n-1) + fib(n-2)


def main():
    print(foo(4, 3))
    print(foo(4, 3, 2))
    print(foo(4, 3))
    print("foo was called", foo.calls, "times")

    print(bar(4, 3))
    print(bar(4, 3, 2))
    print(bar(4, 3, 2, 1))
    print("bar was called", bar.calls, "times")

    print(fib.__doc__)
    fib(3)
    print(fib.calls, 'calls made')


if __name__ == '__main__':
    main()
