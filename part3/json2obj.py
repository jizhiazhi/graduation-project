#!/usr/bin/env python3
import json
import numpy as np
import sys
import pandas as pd

input = sys.argv[1]
output = sys.argv[2]

inputjson = json.load(open(input))
n = inputjson.shape[0]
for i in range(n):
    coor = inputjson[i][0].copy()
    coor = np.matrix(coor).reshape((len(coor), 3))
    coor = pd.DataFrame(coor, columns=['x', 'y', 'z'])
    coor['y'] = coor['y']
    coor.insert(0,'t','v')

    f = inputjson[i][1].copy()
    f = np.matrix(f).reshape((len(f), 3))
    f = pd.DataFrame(f, columns=['x', 'y', 'z'])
    f.insert(0, 't', 'f')
    f['x'] = f['x'] + 1
    f['y'] = f['y'] + 1
    f['z'] = f['z'] + 1
    f = f.astype(str)
    
    obj = pd.concat((coor,f))
    obj.to_csv(f'{output}-{i}.obj',sep=' ',header=False, index=False,index_label=False)
    #else:
        #a.to_csv(f'{output}-none.obj',sep=' ',header=False, index=False,index_label=False)

