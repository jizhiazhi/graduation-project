#!/usr/bin/env python3
import numpy as np
import sys
from xml.dom.minidom import parse
import xml.dom.minidom
import pydoc
import xml.etree.ElementTree as ET

#ci = sys.argv[1]


'''C:/Users/jizhi1/Desktop/untitled.xml'''
DOMTree = ET.parse('C:/Users/jizhi1/Desktop/涡虫配准结果/mask_image/12hpa2/12hpa2.xml')
collection = DOMTree.getroot()


DOMTree2 = ET.parse('C:/Users/jizhi1/Desktop/涡虫配准结果/colour_image/12hpa2/untitled.xml')
collection2 = DOMTree2.getroot()


for item in collection.iter("t2_patch"):
    for item2 in collection2.iter("t2_patch"):
        oid = item.attrib['oid']
        oid2 = item2.attrib['oid']
        if oid == oid2 :
            item2.set('transform',item.attrib['transform'])


tree=ET.ElementTree(collection2) # root为修改后的root
tree.write("C:/Users/jizhi1/Desktop/涡虫配准结果/colour_image/12hpa2/12hpa2.xml")


'''for patch in patchs:
    for patch2 in patchs2:

        if patch.hasAttribute("oid"):
            oid = patch.getAttribute("oid")
        if patch.hasAttribute("transform"):
            transform = patch.getAttribute("transform")

        if patch2.hasAttribute("oid"):
            oid2 = patch2.getAttribute("oid")

        if patch.hasAttribute("transform"):
            transform2 = patch2.getAttribute("transform")
            if oid == oid2:
                patch2.setAttribute("transform",transform)

        if patch.hasAttribute("transform"):
            print(patch2.getAttribute("transform"))

tree=ET.ElementTree(patchs2)  # root为修改后的root
tree.write("C:/Users/jizhi1/Desktop/涡虫配准结果/ss_border_image/WT/untitled2.xml")'''


