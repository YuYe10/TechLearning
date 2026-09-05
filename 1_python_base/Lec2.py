from operator import add, mul
from math import pi
print(pi)
f = max
print(type(f))
print(type(add))

def square(x):
    return mul(x, x)

print(square)
#Question 1
f = min
f = max #f equals to max
g, h = min, max #g equals to min, h equals to max 
max = g # max equals to min
a = max(f(2, g(h(1, 5), 3)), 4)
print(a)

