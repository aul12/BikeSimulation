def sqrt(x):
    import sympy
    import math

    if isinstance(x, sympy.Expr):

        return sympy.sqrt(x)
    else:
        return math.sqrt(x)
