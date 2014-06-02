"""Takes the output from 7X7endpointMatch.py called Modifiedf0MipEndpoints7X7.pckle and grabs the neighbors of the listed points. 
Need to know the configurations of the neighbors to identify whether ir not the endpoint chosen or the point next to it is 
the actual endpoint. The output is saved as Configuration7X7.pckle and contains the neighbors of the identified true endpoints, 
whether it is the original point or replaced by a neighbor in endpointMatch.py. Gets the 7X7X7 neighborhood of the neighbors"""

import os
import sys
sys.path.append('../../vasctrees')
import nxvasc
import cPickle
import numpy as na
import scipy
import math
import imageTools.ITKUtils.io as io
        
#Read in modified .pckle file from 7x7endpointMatch.py
endpoints=open('Modifiedf0MipEndpoints.pckle','rb')
crds=cPickle.load(endpoints)
img= io.readImage('PE00014Filter0_seg.mha',  returnITK=False,  imgMode='uchar')
mask = na.where(img>0, 1, 0) #create the mask
instance=nxvasc.nxvasc()#create an instance of the class
output=open("Configuration7x7.pckle", 'wb') 
instance.setMask(mask) 
instance.createMaskDictionary() 
instance.get7x7matrix() 
#get the crds of all pts within the 7x7 neighborhood of index (i) 
Neighbors=[] #to store arrays of neighbors for each point
for crd in crds:  
    neighbors = mask[crd[2]-3:crd[2]+4, crd[1]-3:crd[1]+4,  crd[0]-3:crd[0]+4]
    Neighbors.append(neighbors)
cPickle.dump([Neighbors, crds],  output) 


    


    

    
    
    

