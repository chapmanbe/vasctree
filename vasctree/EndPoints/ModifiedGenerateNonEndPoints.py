"""The purpose of this code is to perform random sampling of non-endpoints
and grab the 7x7 neighborhoods"""
import os
import sys
sys.path.append("../vasctrees")
import nxvasc
from sliceOrientation import OrientMask
import imageTools.ITKUtils.io as io
import scipy.ndimage as ndi
import numpy as na
import cPickle

fle=open("PE00001NonEndpoints.pckle",'wb')
output2=open("PE00001NeighborsNonPoints7x7.pckle", 'wb')
img=io.readImage("PE00001Filter0_seg.mha", returnITK=False, imgMode="uchar")
#Must create the mask so we can identify the points that are not endpoints
mask=na.where(img>0, 1, 0)
point=nxvasc.nxvasc()
point.setMask(mask)
point.createMaskDictionary()
point.get7x7matrix()
f1=ndi.distance_transform_cdt(img)
surface=na.where(f1==1,1,0)
indsSurface =na.nonzero(surface.flat==1)[0]
length=len(indsSurface)
print "length",length
ModifiedSampledPoints=[]
ModifiedPoints=[]
points=[]
for i in indsSurface:
    if len(ModifiedPoints)<112:
        crds=point.get_crds(i)
        print crds
        #get the neighbors to add up the neighborhood
        neighbor = mask[crds[2]-3:crds[2]+4,crds[1]-3:crds[1]+4,crds[0]-3:crds[0]+4]
        if len(neighbor)<7:
            pass
        else:
            om=OrientMask(neighbor)
            om.orient()
            ModifiedPoints.append(om.mask)
            points.append(i)
    else:
        pass
#points=indsSurface[552:664]
print "output",  points
cPickle.dump(points,fle)
print "M=", len(ModifiedPoints)
cPickle.dump(ModifiedPoints,  output2)

    
