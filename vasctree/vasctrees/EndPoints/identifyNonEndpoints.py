
#identifyNonEndpoints.py
"""Grabs the 3x3 neighborhoods on the non endpoints"""
import os
import sys
sys.path.append("../vasctrees")
import numpy as na
import random
import cPickle
import imageTools.ITKUtils.io as io
import nxvasc
from sliceOrientation import OrientMask

img = io.readImage("PE00001Filter0_seg.mha",  returnITK=False,  imgMode="uchar")
nonPoints=open("PE00001NonEndpoints.pckle", 'rb')
nonendpoints=cPickle.load(nonPoints)
output2=open("PE00001NeighborsNonPoints3x3.pckle", 'wb')
#Must create the mask so we can identify the points that are not endpoints
mask=na.where(img>0, 1, 0)
point=nxvasc.nxvasc()
point.setMask(mask)
point.createMaskDictionary()
point.get3x3matrix()
crds=point.get_crds(nonendpoints)
ModifiedSampledPoints=[]
ModifiedPoints=[]
for crd in crds:
    print crd
    #get the neighbors to add up the neighborhood
    neighbors = mask[crd[2]-1:crd[2]+2, crd[1]-1:crd[1]+2, crd[0]-1:crd[0]+2]
    print neighbors
    ModifiedSampledPoints.append(neighbors)
for M in ModifiedSampledPoints:  
    #print M
    if len(M)<3:
        pass
    else:
        om=OrientMask(M)
        om.orient()
        ModifiedPoints.append(om.mask)
print "M=", len(ModifiedPoints)
cPickle.dump(ModifiedPoints,  output2)
