import sympy
import math


def sqrt(x):
    if isinstance(x, sympy.Expr):
        return sympy.sqrt(x)
    else:
        return math.sqrt(x)


def cos(x):
    if isinstance(x, sympy.Expr):
        return sympy.cos(x)
    else:
        return math.cos(x)
