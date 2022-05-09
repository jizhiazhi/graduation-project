#!/usr/bin/env python3
import numpy as np
import pandas as pd
import argparse

def main(args):

    #load offset
    offset = '/dellfsqd2/ST_OCEAN/USER/huangzhi/wt/3d_atlas/step01/paste_pre/offset.txt'
    offset = pd.read_csv(offset, sep='\t',header=0, compression='infer', comment='#')
    offset = offset.set_index('ID')
    print(args.slice)
    offset_x = int(offset.loc[args.slice,'x'])
    offset_y = int(offset.loc[args.slice,'y'])

    #section bin
    gemc = pd.read_csv(args.gem, sep='\t', header=0, compression='infer', comment='#')
    gemc = gemc[['geneID','x','y','MIDCounts']]
    gemc['x'] = gemc['x'].astype('float')
    gemc['y'] = gemc['y'].astype('float')
    gemc['x'] = gemc['x']- offset_x
    gemc['y'] = gemc['y']- offset_y
    max_x = gemc['x'].max()
    max_y = gemc['y'].max()
    gemc['x'] = gemc['x']/args.bin
    gemc['y'] = gemc['y']/args.bin
    gemc['x'] = gemc['x'].astype('int')
    gemc['y'] = gemc['y'].astype('int')
    gemc['x'] = gemc['x']*args.bin
    gemc['y'] = gemc['y']*args.bin

    #96gene
    if args.marker:
        print('use the special 96 marker genes')
        geneID = pd.read_csv('/dellfsqd2/ST_OCEAN/USER/huangzhi/wt/3d_atlas/step01/paste_pre/geneID.txt', sep='\t', header=0, compression='infer', comment='#')
        gemc = pd.merge(gemc,geneID)

    #output bincell coor
    gemc['bincell'] = gemc['x'].astype('str') + gemc['y'].astype('str')
    cell_coor = gemc[['x','y','bincell']]
    cell_coor = cell_coor.drop_duplicates()
    coor = cell_coor[['x','y']]
    coor.to_csv(f'{args.output}_coor.csv', sep=',', header=False, index=False)

    gemc_data = gemc[['geneID','bincell','MIDCounts']]
    gemc_data = gemc_data.groupby(['geneID', 'bincell']).agg(UMI_sum=('MIDCounts', 'sum')).reset_index()
    gene_list = gemc_data['geneID']
    cell_list = cell_coor['bincell']
    gene_list = gene_list.drop_duplicates()

    #frame to matrix
    matrix = np.zeros(shape=(len(cell_list),len(gene_list)))
    cell_list = cell_list.to_frame()
    gene_list = gene_list.to_frame()
    cell_list.insert(1, 'y', range(len(cell_list)), allow_duplicates=False)
    gene_list.insert(1, 'x', range(len(gene_list)), allow_duplicates=False)

    gemc_data = pd.merge(gemc_data,cell_list)
    gemc_data = pd.merge(gemc_data,gene_list)

    matrix[gemc_data['y'],gemc_data['x']]=gemc_data['UMI_sum']


    #cover percentage
    if args.cover:
        print('filte cover percentage {args.cover} genes')
        matrix_fil = matrix.copy()
        matrix_fil[matrix_fil>0] = 1
        fil = np.sum(matrix_fil,axis=0)
        fil = fil.T
        matrix = matrix.T
        matrix = matrix[fil<int(matrix_fil.shape[0]*args.cover)]
        matrix = matrix.T

    #top
    if args.top:
        print(f'filter top {args.top} genes')
        matrix_fil = np.zeros((matrix.shape[0],matrix.shape[1]))
        for i in range(matrix.shape[0]):
            single_bin = matrix[i]
            top = np.argpartition(single_bin, -args.top)[-args.top:]
            matrix_fil[i,top]=matrix[i,top]
        idx = np.argwhere(np.all(matrix_fil[..., :] == 0, axis=0))
        matrix = np.delete(matrix_fil, idx, axis=1)

    #give name
    name = list(range(matrix.shape[1]))
    for i in range(len(name)):
        name[i] = 'gene' + str(name[i])

    cellname = list(range(matrix.shape[0]))
    for i in range(len(cellname)):
        cellname[i] = 'cell' + str(cellname[i])

    matrix = pd.DataFrame(matrix,columns=name,index=cellname)
    matrix.to_csv(f'{args.output}_matrix.csv', sep=',', header=True, index=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="-g -s are necessary, -t -c -m are the different functions to filter genes")
    parser.add_argument("-g", "--gem", help="the path of gem file", type=str, default='', nargs='?')
    parser.add_argument("-s", "--slice", help="the slice name what you want, like 22-WT", type=str, default='', nargs='?')
    parser.add_argument("-b", "--bin", help="bin_size, default 20", type=int, default=20, nargs='?')
    parser.add_argument("-t", "--top", help="the top N genes in every bins", type=int, default=False, nargs='?')
    parser.add_argument("-c", "--cover", help="retain the genes which cover bin of percentage N ", type=float, default=False, nargs='?')
    parser.add_argument("-m", "--marker", help="use the special marker genes", action='store_true', default = False)
    parser.add_argument("-o", "--output", help="directory to save files", default='output')
    args = parser.parse_args()
    main(args)

