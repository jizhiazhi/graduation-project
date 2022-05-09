#!/usr/bin/env python3
from xml.dom.minidom import parse
import xml.dom.minidom
import numpy as np
import sys



ci = sys.argv[1]


'''C:/Users/jizhi1/Desktop/untitled.xml'''
DOMTree = xml.dom.minidom.parse(ci)
collection = DOMTree.documentElement
patchs = collection.getElementsByTagName("t2_patch")

json_list = []
for patch in patchs:

    patch_list = []
    if patch.hasAttribute("title"):
        tit = patch.getAttribute("title")
        patch_list.append(tit)
    if patch.hasAttribute("transform"):
        transform = patch.getAttribute("transform")
        transform = transform[7:-1]
        patch_list.append(transform)
    json_list.append(patch_list)

json_list=str(json_list).replace("'","\"")
print(json_list)