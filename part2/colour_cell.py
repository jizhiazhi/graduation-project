#!/usr/bin/env python3

import numpy as np
import getopt
import sys
import pandas as pd
from skimage import io
import json

#####################################################
def merge_colour_usage():
    print("""
Usage :  python3  colour_mask3.py  \\
            -s <seurat cluster file> \\
            -c <colour json file> \\
            -o <output prefix> \\
            -m <mask file> \\
            -d <slice id>
""", flush=True)

#####################################################
def merge_colour_main(argv:[]):
    prefix = ''
    cluster_file = ''
    colour_file = ''
    mask_file = ''
    slice_id = ''

    try:
        opts, args = getopt.getopt(argv,"h:c:s:o:m:d:",["help","colour","seurat_cluster=","output=","mask=","id="])
    except getopt.GetoptError:
        merge_colour_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            merge_colour_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-s", "--seurat_cluster"):
            cluster_file = arg
        elif opt in ("-c", "--colour"):
            colour_file = arg
        elif opt in ("-m", "--mask"):
            mask_file = arg
        elif opt in ("-d", "--id"):
            slice_id = arg

    if cluster_file != "" and prefix != ""  and mask_file != "" and slice_id != "" and colour_file != "":
        print(f'{slice_id} start')
        # load cell position masks
        mask_image = np.loadtxt(mask_file)
        # load colour map
        colour = json.load(open(colour_file))
        colour_pd = pd.DataFrame(columns=['cluster','r','g','b'])
        i = 0
        for cinfo in colour:
            colour_pd.loc[i]= [cinfo[0],cinfo[1][0],cinfo[1][1],cinfo[1][2]]
            i = i +1           
        # load cluster of this slice
        cluster = pd.read_csv(cluster_file, sep='\t', header=0, compression='infer', comment='#')
        slice_cluster = cluster[cluster['orig.ident'] == slice_id]
        # get cell-cluster-colour dataframe
        ccc=pd.DataFrame()
        ccc['cell']=slice_cluster['cell']
        ccc['cluster']=slice_cluster['seurat_clusters']
        y , x = np.where(mask_image!=0)
        # join colour and cluster positions
        ccc = ccc.set_index('cluster')
        colour_pd = colour_pd.set_index('cluster')
        ccc = ccc.join(colour_pd,how='inner')
        # get cell-x,y dataframe
        value = mask_image[y,x]
        pdata = pd.DataFrame()
        pdata['x'] = x
        pdata['y'] = y
        pdata['cell'] = value 
        # join colour and x,y positions
        pdata= pdata.set_index('cell')
        ccc= ccc.set_index('cell')
        draw_data = ccc.join(pdata,how='inner')
        # draw tif
        new_data = np.zeros((mask_image.shape[0], mask_image.shape[1], 3), dtype=int)
        new_data[draw_data['y'],draw_data['x'],0] = draw_data['r'] 
        new_data[draw_data['y'],draw_data['x'],1] = draw_data['g'] 
        new_data[draw_data['y'],draw_data['x'],2] = draw_data['b'] 
        new_data = new_data.astype('uint8')
        io.imsave(f'{prefix}.tif',new_data)
    else:
        merge_colour_usage()
        sys.exit(1)

#####################################################
if __name__ == '__main__':
    merge_colour_main(sys.argv[1:])


