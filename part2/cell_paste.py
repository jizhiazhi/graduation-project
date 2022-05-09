#!/usr/bin/env python3
import numpy as np
import pandas as pd
import sys


def mask2coor(cell_mask):
    cell_position = np.loadtxt(cell_mask)
    y, x = np.where(cell_position != 0)
    value = cell_position[y, x]
    pdata = pd.DataFrame()
    pdata['x'] = x
    pdata['y'] = y
    pdata['cell'] = value
    cell = pdata.groupby(['cell']).agg(x=('x', 'mean'), y=('y', 'mean')).reset_index()

    max_x = cell['x'].max()
    max_y = cell['y'].max()
    min_x = cell['x'].min()
    min_y = cell['y'].min()
    x_box = (max_x - min_x) / 10
    y_box = (max_y - min_y) / 10

    bin_data = pd.DataFrame(columns=['cell', 'x', 'y', 'bincell'])
    for i in range(10):
        for j in range(10):
            data = cell[cell['x'] >= (min_x + x_box * j)]
            data = data[data['x'] < (min_x + x_box * (j + 1))]
            data = data[data['y'] >= (min_y + y_box * i)]
            data = data[data['y'] < (min_y + y_box * (i + 1))]
            data.insert(3, 'bincell', j + 10 * i, allow_duplicates=False)
            bin_data = bin_data.append(data)

    bin_cell_coor = bin_data.groupby(['bincell']).agg(x=('x', 'mean'), y=('y', 'mean')).reset_index()
    cell2bin = bin_data[['cell','bincell']]
    return cell2bin,bin_cell_coor

input_cell = sys.argv[1]
input_gemc = sys.argv[2]
output = sys.argv[3]

#load
cell_mask = input_cell
gemc = input_gemc

cell2bin,bin_cell_coor = mask2coor(cell_mask)
gemc_data = pd.read_csv(gemc, sep='\t', header=0, compression='infer', comment='#')
gemc_data = pd.merge(gemc_data,cell2bin)

coor = bin_cell_coor.copy()
coor = coor[['x','y']]
coor.to_csv(f'{output}_coor.csv', sep=',', header=False, index=False)

gemc_data = gemc_data[['geneID','bincell','MIDCounts']]
gemc_data = gemc_data.groupby(['geneID', 'bincell']).agg(UMI_sum=('MIDCounts', 'sum')).reset_index()

gene_list = gemc_data['geneID']
cell_list = bin_cell_coor['bincell']

gene_list = gene_list.drop_duplicates()



matrix = np.zeros(shape=(len(cell_list),len(gene_list)))

cell_list = cell_list.to_frame()
gene_list = gene_list.to_frame()
cell_list.insert(1, 'y', range(len(cell_list)), allow_duplicates=False)
gene_list.insert(1, 'x', range(len(gene_list)), allow_duplicates=False)


gemc_data = pd.merge(gemc_data,cell_list)
gemc_data = pd.merge(gemc_data,gene_list)

matrix[gemc_data['y'],gemc_data['x']]=gemc_data['UMI_sum']

matrix = pd.DataFrame(matrix,columns=gene_list['geneID'])

matrix.to_csv(f'{output}_matrix.csv', sep=',', header=True, index=False)
