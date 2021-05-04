# Code from the SLSH_pyhthon_akshat repository.

import numpy as np

def predict(q, i, f_query, tables, k = 5, func = np.median):
    res = np.array(f_query(q, tables, k))

    print("CANDIDATES")
    print(res[:,:5])

    return func(res[:,i])
