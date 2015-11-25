#5x5Config_of_Endpoints.py

"""Takes the output from 5x5endpointMatch.py called Modifiedf0MipEndpoints5x5.pckle
and grabs the neighbors of the listed points. 
Need to know the configurations of the neighbors to identify whether ir not the
endpoint chosen or the point next to it is the actual endpoint. The output is saved
as Configuration5x5.pckle and contains the neighbors of the identified true endpoints, 
whether it is the original point or replaced by a neighbor in 5x5endpointMatch.py.
Gets the 5x5x5 neighborhood of the neighbors"""

import os
import sys
sys.path.append('../')
import nxvasc
import cPickle
import numpy as na
import scipy
import math
import imageTools.ITKUtils.io as io
        
#Read in modified .pckle file from 5x5endpointMatch.py
endpoints=open('Modifiedf0MipEndpoints5x5.pckle','rb')
crds=cPickle.load(endpoints)
img= io.readImage('PE00026Filter0_seg.mha',  returnITK=False,  imgMode='uchar')
mask = na.where(img>0, 1, 0) #create the mask
instance=nxvasc.nxvasc()#create an instance of the class
output=open("Configuration5x5.pckle", 'wb') #Need to store the output for the 5x5 
instance.setMask(mask) #Set the mask using the numpy image mask. In addition to
#reading the mask, the 1D indicies into the 3D image are generate and stored
instance.createMaskDictionary() #Create dictionary that maps the index into the 3D
#volume to an index into the mask. The 1D array into the 3D volume is the key &
#the ordinal position of the index is the value
instance.get5x5matrix() #define relationship between neighbors
#get the crds of all pts within the 5x5 neighborhood of index (i) 
Neighbors=[] #to store arrays of neighbors for each point
for crd in crds:  \
    #grab the 5x5x5 neighborhood 
    neighbors = mask[crd[2]-2:crd[2]+3, crd[1]-2:crd[1]+3,  crd[0]-2:crd[0]+3]
    Neighbors.append(neighbors)
cPickle.dump([Neighbors, crds],  output) 


    


    

    
    
    

