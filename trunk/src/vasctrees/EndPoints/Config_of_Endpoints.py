"""Takes the output from endpointMatch.py called Modifiedf0MipEndpoints.pckle and grabs the neighbors of the listed points. 
Need to know the configurations of the neighbors to identify whether ir not the endpoint chosen or the point next to it is 
the actual endpoint. The output is saved as Configuration.pckle and contains the neighbors of the identified true endpoints, 
whether it is the original point or replaced by a neighbor in endpointMatch.py. Gets the 3x3x3 neighborhood of the neighbors"""

import os
import sys
#import vasctrees.nxvasc as nxvasc
sys.path.append('../')
import nxvasc
import cPickle
import numpy as na
import scipy
import math
import imageTools.ITKUtils.io as io
import dicom

#Read in modified .pckle file
endpoints=open('Modifiedf0MipEndpoints.pckle','rb')
#endpoints=sys.argv[1]
#fo = open(endpoints,'rb')
#print endpoints
crds=cPickle.load(endpoints)
#Read in image
#img= io.readImage(str(sys.argv[2]),  returnITK=False,  imgMode='uchar')
img= io.readImage('PE00026Filter0_seg.mha',  returnITK=False,  imgMode='uchar')
#img=open('PE00026Filter0_seg.dcm','rb')
mask = na.where(img>0, 1, 0) #create the mask
point=nxvasc.nxvasc() #create an instance of the class
output=open("Configuration.pckle", 'wb') #Need to store the output

point.setMask(mask) #Set the mask using the numpy image mask. In addition to
#reading the mask, the 1D indicies into the 3D image are generate and stored

point.createMaskDictionary() #Create dictionary that maps the index into the 3D
#volume to an index into the mask. The 1D array into the 3D volume is the key &
#the ordinal position of the index is the value

point.get3x3matrix() #define relationship between neighbors
inds=point.getInds(crds)#get corresponding indexes

#get the crds of all pts within the 3x3 or 26-point neighborhood of index (i) 
Neighbors=[] #to store arrays
for crd in crds:   
    #grab the 3x3x3 neighborhood 
    neighbors = mask[crd[2]-1:crd[2]+2, crd[1]-1:crd[1]+2,  crd[0]-1:crd[0]+2]
    Neighbors.append(neighbors)
    
cPickle.dump([Neighbors, crds],  output) 



    

    
    
    

