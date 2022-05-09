#!/usr/bin/env python3
import math
from skimage import io
import numpy as np
import pandas as pd
from scipy.spatial import distance
from scipy.spatial import KDTree
import argparse
import json

def getCurveY(xvals0,xvals1,xvals2,x1,x2,y1,y2,k):
    yvals0 = np.polyval(k, xvals0)

    k1 = k[2]+2*k[1]*x1+3*k[0]*x1*x1
    b1 = y1 - k1*x1
    k1 = [k1,b1]
    yvals1 = np.polyval(k1, xvals1)

    k2 = k[2]+2*k[1]*x2+3*k[0]*x2*x2
    b2 = y2 - k2*x2
    k2 = [k2,b2]
    yvals2 = np.polyval(k2, xvals2)

    yvals = np.hstack((yvals1, yvals0, yvals2))

    return yvals,k1,k2

def main(args):
    #load parameter and constrain
    c = pd.read_csv('constrain.txt', sep='\t')
    c = c.set_index('id')
    p = pd.read_csv('line_parameter.txt', sep='\t')
    p = p.set_index('id')
    s = pd.read_csv("shift.csv",sep='\t',names = ['id','shift'])
    s = s.set_index('id')


    name = args.name
    #load line
    x1 = c.loc[name, 'x1']*0.5
    x2 = c.loc[name, 'x2']*0.5
    y1 = c.loc[name, 'y1']*0.5
    y2 = c.loc[name, 'y2']*0.5
    k = [p.loc[name, 'k0']*2*2, p.loc[name, 'k1']*2, p.loc[name, 'k2'], p.loc[name, 'k3']*0.5]
    shift = s.loc[name, 'shift']

    # line_new_points
    xvals0 = np.arange(x1,x2,0.1)
    xvals1 = np.arange(0,x1,0.1)
    xvals2 = np.arange(x2,x2+500,0.1)
    x = np.hstack((xvals1,xvals0,xvals2))

    line_new_points = np.zeros((len(x),2))
    line_new_points[:,0] = x
    y,k1,k2 = getCurveY(xvals0,xvals1,xvals2,x1,x2,y1,y2,k)
    line_new_points[:,1] = y

    # calc distance of curve as new x
    length = np.zeros(len(line_new_points))
    for i in range(1,len(line_new_points)):
        length[i] = distance.euclidean(line_new_points[i,:],line_new_points[i-1,:])
    length = np.cumsum(length)

    # load raw points
    obj = json.load(open(args.meshfile))
    new_list = []
    for i in range(4):
        coor = obj[i][0].copy()
        coor = np.matrix(coor).reshape((len(coor), 3))
        raw = pd.DataFrame(coor, columns=['x', 'y', 'z'])
        index = list(range(len(raw)))
        raw['index'] = index
        raw0 = raw[(raw['x']<=x2)&(raw['x']>=x1)].copy()
        raw1 = raw[raw['x']<x1].copy()
        raw2 = raw[raw['x']>x2].copy()
        raw0['y_inline'] = np.polyval(k, raw0['x'])
        raw1['y_inline'] = np.polyval(k1, raw1['x'])
        raw2['y_inline'] = np.polyval(k2, raw2['x'])
        raw = pd.concat([raw0,raw1,raw2], axis=0, ignore_index=True)
        raw['up'] = raw['y']>=raw['y_inline']
        raw['down'] = raw['y']<raw['y_inline']
        raw = raw.sort_values('index',ascending = True)

        # get clost point for all raw points
        kdtree = KDTree(np.array(line_new_points))
        raw_pos = np.zeros((len(raw),2))
        raw_pos[:,0] = raw['x']
        raw_pos[:,1] = raw['y']
        darray, iarray = kdtree.query(raw_pos)

        # get new nx ny
        raw['ny'] = darray
        new_y = np.zeros(len(raw['ny']))
        new_y[raw['up'] ]  = raw[raw['up']]['ny']
        new_y[raw['down']] = -raw[raw['down']]['ny']
        raw['ny'] = new_y
        raw['nx'] = length[np.array(iarray).astype(int)]
        new = pd.DataFrame()
        new[['x','y','z']] = raw[['nx','ny','z']]

        coor = np.matrix(new).reshape((len(new), 3))
        coor = coor.tolist()
        f = obj[i][1].copy()
        cf_list = []
        cf_list.append(coor)
        cf_list.append(f)
        new_list.append(cf_list)

    out = open(f'{args.output}.json', 'w')
    print(new_list, file=out)
    out.close()



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", help="the name of sample,like WT", type=str, default='', nargs='?')
    parser.add_argument("-m", "--meshfile", help="input pos file path", type=str, default='', nargs='?')
    #parser.add_argument("-c", "--constrain", help="constrain file path", type=str, default='', nargs='?')
    #parser.add_argument("-d", "--define", help="Domain definition, x_max x_min y_max y_min", type=str, default=[], nargs='+')
    parser.add_argument("-o", "--output", help="directory to save files", type=str,default='output')
    args = parser.parse_args()
    main(args)
