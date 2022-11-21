import numpy as np
import finddep as fd

a = [1,2,3,4,5,6]
b = [1,2,1,2,2,1]

link_type = fd.find_dep(a,b)

print(f'find_dep({a}, {b}) = {link_type}')


