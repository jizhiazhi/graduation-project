#!/usr/bin/env python3

import numpy as np
import getopt
import sys
import pandas as pd
from skimage import io
import json
import scipy.ndimage as nd

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
def RGB2wh(img):
    new_data = np.zeros((img.shape[0],img.shape[1]), dtype=int)
    new_data = new_data + img[:, :, 0]
    #new_data = new_data + img[:, :, 1]
    #new_data = new_data + img[:, :, 2]
    #new_data = (new_data) / 3
    new_data = new_data.astype('uint8')
    return new_data

def resize(img,bin):
    img = img.copy()
    y,x = np.where(img!=0)
    x_t = ((x/bin).astype('int'))
    y_t = ((y/bin).astype('int'))
    w = int(img.shape[1]/bin)+1
    h = int(img.shape[0]/bin)+1
    x_t[x_t>=w] = w-1
    y_t[y_t>=h] = h-1
    result = np.zeros((h,w),dtype='uint8' )
    pdata = pd.DataFrame()
    pdata['x'] = x
    pdata['y'] = y
    pdata['x_t'] = x_t
    pdata['y_t'] = y_t
    pdata['value'] = img[y,x]
    result[pdata['y_t'],pdata['x_t']] = pdata['value']

    return result


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
        slice_cluster = cluster[cluster['a'] == slice_id]
        # get cell-cluster-colour dataframe
        ccc=pd.DataFrame()
        ccc['cell']=slice_cluster['b']
        ccc['cluster']=slice_cluster['c']
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
        new_data = RGB2wh(new_data)
        #gut = new_data[new_data==55].copy()
        neural = new_data.copy()
        neural[neural!=150]=0
        other = new_data.copy()
        other[other!=0]=5
        new_data[new_data==5]=0
        new_data[new_data==150]=0
        #pharynx = new_data[new_data==255].copy()
        #gut = resize(gut,14)
        neural = resize(neural,14)
        other = resize(other,14)
        #pharynx = resize(pharynx,14)

        forward_affine = np.matrix([[1.0/float(14),0,0],[0,1.0/float(14),0],[0,0,1]])
        affineR = forward_affine.I
        #print(new_data.shape)
        w = int(new_data.shape[1]/14)+1
        h = int(new_data.shape[0]/14)+1
        affined_mask = nd.affine_transform(new_data.T,affineR,output_shape=(w,h),order=0)
        new_data = affined_mask.T
        
        new_data[neural == 150 ] = 150
        new_data = new_data+other

        io.imsave(f'{prefix}.tif',new_data)
    else:
        merge_colour_usage()
        sys.exit(1)

#####################################################
if __name__ == '__main__':
    merge_colour_main(sys.argv[1:])





#!/usr/bin/env python3
