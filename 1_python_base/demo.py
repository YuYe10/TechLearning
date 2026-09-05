from math import pi, sqrt

def area(r, shape_constant=pi):
    """Return the area of a shape from length measurement r.

    >>> area(2)
    4.0
    >>> area(5)
    78.53981633974483
    """
    assert r > 0, 'A length must be positive'
    return r * r * shape_constant