#!/usr/bin/env python3
import os
import sys
import time
import json
import getopt
import numpy as np
import pandas as pd
import scipy.ndimage as nd
from subprocess import check_call
from skimage import io as skio
import skimage.morphology as sm
from skimage import filters

def gem_to_cfm_usage():
    print("""
Usage : GEM_toolkit.py gem_to_cfm               -s <ssdna tiff file> \\
                                                -e <expanding the radius of one pixel, default 9>\\
                                                -v <use value to increase or decrease the threshold, apply threhold = auto threshold + value, default 0>\\
                                                -h [show this usage]\\
                                                -o <output prefix>
Notice:  
    -s ssdna.tif -o output 
    function: ssdna to mask with specific manner
""",flush=True)




def get_mask(ssdna_file,prefix,value,expand):
    ssdna = skio.imread(ssdna_file)

    if len(ssdna.shape) == 3:  # RGB tiff to 8 bit gray tiff
        new_data = np.zeros((ssdna.shape[0], ssdna.shape[1]), dtype=int)
        new_data = new_data + ssdna[:, :, 0]
        new_data = new_data + ssdna[:, :, 1]
        new_data = new_data + ssdna[:, :, 2]
        ssdna = new_data.astype('uint8')

    # ssdna =sfr.enhance_contrast(ssdna, sm.disk(9))
    # ssdna =sfr.enhance_contrast(ssdna, sm.disk(3))

    #convert to mask
    thre = filters.threshold_otsu(ssdna)
    print("the auto-set threshold is :",thre)
    print("the value you want to increase is :",value)
    thre = thre + int(value)
    if thre > 255:
        thre = 255
    elif thre < 0:
        thre = 0
    else:
        thre = thre
    
    print("the threshold what you set is :",thre)
    
    ssdna[ssdna >= thre] = 255
    ssdna[ssdna < thre] = 0

    #expand pixel
    ssdna_dilation = sm.dilation(ssdna, sm.disk(int(expand)))
    # ssdna_dilation=sm.dilation(ssdna_dilation,sm.square(5))
    # edges = edges.astype('uint8')
    # print(edges)
    # edges = edges.astype('uint8')'''

    skio.imsave(f'{prefix}.mask.tif', ssdna_dilation)
    return ssdna_dilation

def gem_to_cfm_main(argv:[]):
    prefix = ''
    ssdna = ''
    expand = 9
    value = 0
    
    try:
        opts, args = getopt.getopt(argv,"ho:s:e:v",["help","output=","ssdna=","expand","value"])
    except getopt.GetoptError:
        gem_to_cfm_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            gem_to_cfm_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-s", "--ssdna"):
            ssdna = arg
        elif opt in ("-e", "--expand"):
            expand = arg
        elif opt in ("-v", "--value"):
            value = arg



    if ssdna != ""  and prefix != "" and value != "" and expand != "":
        get_mask(ssdna,prefix,value,expand)

    else:
        gem_to_cfm_usage()
        sys.exit(3)



if __name__ == "__main__":
    gem_to_cfm_main(sys.argv[1:])
    print('all file has been saved')
    print(time.strftime("%Y-%m-%d %H:%M:%S"), file=sys.stderr, flush=True)
