import os
import sys
#sys.path.append('../../vasctrees')
import vasctrees.nxvasc as nxvasc
import cPickle
import numpy as na
import scipy
import math
import imageTools.ITKUtils.io as io
import matplotlib.pyplot as pyplot
import pylab

def showPoints(point, neighbors):
    #get the orthogonal (x,y,z) MIPS of the mask.
    #Also compute the depth buffers for each MIP
#    mipz = neighbors.max(axis=0)
#    mipy = neighbors.max(axis=1)
#    mipx = neighbors.max(axis=2)
    slice0 = neighbors[0, :, :]
    slice1 = neighbors[1, :, :]
    slice2 = neighbors[2, :, :]
    pyplot.gray() #default color scheme
    
    #Plot the three views
    pyplot.subplot(221) 
    pyplot.imshow(slice0,  interpolation = 'nearest')
    pyplot.title("mipz")
    pyplot.subplot(222)
    pyplot.imshow(slice1,  interpolation = 'nearest')
    pyplot.title("mipy")
    pyplot.subplot(223)
    pyplot.title("mipx")
    pyplot.imshow(slice2,  interpolation = 'nearest')
    figure = pyplot.show()
    raw_input('continue')
 
#Read in modified .pckle file
endpoints=open('Modifiedf0MipEndpoints.pckle','rb')
#endpoints=sys.argv[1]
#fo = open(endpoints,'rb')
#crds=cPickle.load(fo)
crds = cPickle.load(endpoints)
#Read in image
#img= io.readImage(str(sys.argv[2]),  returnITK=False,  imgMode='uchar')
img= io.readImage('PE00026Filter0_seg.mha',  returnITK=False,  imgMode='uchar')
mask = na.where(img>0, 1, 0) #create the mask
point=nxvasc.nxvasc() #create an instance of the class
point.setMask(mask) #Set the mask using the numpy image mask. In addition to
#reading the mask, the 1D indicies into the 3D image are generate and stored
point.createMaskDictionary() #Create dictionary that maps the index into the 3D
#volume to an index into the mask. The 1D array into the 3D volume is the key &
#the ordinal position of the index is the value
point.get3x3matrix() #define relationship between neighbors
inds=point.getInds(crds)#get corresponding indexes
#get the crds of all pts within the 3x3 or 26-point neighborhood of index (i) 
for crd in crds:
    #grab the 3x3 neighborhood of i and convert to list
    neighbors = mask[crd[2]-1:crd[2]+2, crd[1]-1:crd[1]+2,  crd[0]-1:crd[0]+2]  
    #plot=showPoints(point, neighbors)
#    get the orthogonal (x,y,z) MIPS of the mask.
#    mipz = neighbors.max(axis=0)
#    mipy = neighbors.max(axis=1)
#    mipx = neighbors.max(axis=2)
    slice0 = neighbors[0, :, :]
    slice1 = neighbors[1, :, :]
    slice2 = neighbors[2, :, :]   
    #Plot the three views
    pyplot.subplot(221) 
    pyplot.gray() #default color scheme
    pyplot.imshow(slice0,  interpolation = 'nearest')
    pyplot.title("mipz")
    pyplot.subplot(222)
    pyplot.gray() 
    pyplot.imshow(slice1,  interpolation = 'nearest')
    pyplot.title("mipy")
    pyplot.subplot(223)
    pyplot.gray() 
    pyplot.title("mipx")
    pyplot.imshow(slice2,  interpolation = 'nearest')
    pyplot.savefig("mipConfiguration.png")
    #pyplot.show()
#    #raw_input('continue')
##    fig_output=("mipConfiguration.png", 'wb')
##    figure.write(fig_output)
