#!/usr/bin/env python3
import numpy as np
import pandas as pd
from skimage import io
import scipy.ndimage as nd
import argparse
import os
from numpy import average, linalg, dot
from skimage.metrics import structural_similarity as ssim

def colour_overlap(img1,img2):
    slice1 = img1.copy()
    slice2 = img2.copy()
    slice1[slice1 != 0] = 1
    slice2[slice2 != 0] = 1
    colour_index = slice1 + slice2
    colour = np.zeros((colour_index.shape[0], colour_index.shape[1], 3), dtype='int8')
    colour[slice1 == 1] = [0, 255, 0]
    colour[slice2 == 1] = [255, 0, 0]
    colour[colour_index == 2] = [255, 255, 0]
    return colour

def ssim_compare(slice1,slice2):
    result = ssim(slice1,slice2)
    return result

def overlap_compare(image1,image2):
    slice1 = image1.copy()
    slice2 = image2.copy()
    slice1[slice1 != 0] = 1
    slice2[slice2 != 0] = 1
    max1 = np.sum(slice1)
    max2 = np.sum(slice2)
    match = slice1 + slice2
    match_score = np.sum(match[match==2])/2
    return (match_score/max1+match_score/max2)/2

def cos_compare(image1, image2):
    vector1 = image1.flatten().tolist()
    vector2 = image2.flatten().tolist()
    norm1 = linalg.norm(vector1, 2)
    norm2 = linalg.norm(vector2, 2)
    res = dot(vector1/norm1, vector2/norm2)
    return res


def main(args):
    n_slices = int(len(args.filename))
    score = pd.DataFrame(columns=['image','cos','overlap','ssim'])
    for i in range(n_slices - 1):
        slice1 = io.imread(args.filename[i])
        slice2 = io.imread(args.filename[i + 1])
        matrix = np.matrix(args.matrix[i]).reshape((3,3))
        #re_matrix = np.matrix([[1,0,0],[0,1,0],[0,0,1]])
        if slice1.shape[0]*slice1.shape[1] < slice2.shape[0]*slice2.shape[1]:
           slice1 = nd.affine_transform(slice1.T, matrix, output_shape=(slice2.shape[1],slice2.shape[0]), order=0)
           slice1 = slice1.T
        else:
           slice2 = nd.affine_transform(slice2.T, matrix.I, output_shape=(slice1.shape[1],slice1.shape[0] ), order=0)
           slice2 = slice2.T
        colour = colour_overlap(slice1, slice2)
        score = score.append({'image':f'{i+args.small}-{i+args.small+1}','cos':cos_compare(slice1,slice2),'overlap':overlap_compare(slice1,slice2),'ssim':ssim_compare(slice1,slice2)},ignore_index=True)
        if not os.path.exists(args.output):
           os.mkdir(args.output)
        io.imsave(f'{args.output}/colour{i+args.small}-{i+args.small+1}.tif', colour)
        io.imsave(f'{args.output}/slice{i+args.small}-{i+args.small+1}.tif', slice1)
        io.imsave(f'{args.output}/slice{i+args.small}-{i+args.small+1}.tif', slice2)

        #print(f'{args.filename[i]} and {args.filename[i+1]}')
    score.to_csv(f'{args.output}/score.csv', sep='\t', header=True, index=False)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", help="slice", type=str, default=[], nargs='+')
    parser.add_argument("-m", "--matrix", help="matrix", type=str, default=[], nargs='+')
    parser.add_argument("-s", "--small", help="small", type=int, default=0, nargs='?')
    parser.add_argument("-o", "--output", help="directory to save files", default='output')
    args = parser.parse_args()
    main(args)
