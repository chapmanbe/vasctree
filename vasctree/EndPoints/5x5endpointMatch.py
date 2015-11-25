#5x5endpointMatch.py

"""This code takes as input the f0MipEndpoints.pckle which came from labeled
endpoints.py. In order to know whether or not the labeled points are true
endpoints we muct grab the neighbors of each point and learn their location in
the mask. It returns Modifiedf0MipEndpoints5x5.pckle which will be passed to
5x5Config_of_Endpoints.py The points returned are either the original point
or the neighbor see fxn grabBestendpoint"""

import os 
import sys
sys.path.append("../")
import nxvasc
import cPickle
import numpy as na
import array
import scipy
import math
import imageTools.ITKUtils.io as io
def grabBestEndpoint(neighbors,point):
    """We must go and get the neighbors of the neighbors to determine how
many of the original indexes neighbors are in the mask. The fewer the
neighbors the more likely the point is an endpoint. If a neighbor
is found with fewer neighbors than the original index then it replaces
that point as the new endpoint"""
    minNeighbors=150 #never have a point with 150 neighbors in 124 pt. neighborhood
    BestI=-1 # never have a point that has no neighbors
    for i in neighbors:#get the neighbors that are in the mask
        data=point.getValidNeighborsInformation(point.inds[i]) 
        if len(data[0])< minNeighbors: 
            BestI=i
            #new best point with minneighbors as the total number of neighbors
            minNeighbors=len(data[0])
            #returns the number of neighbors in the mask
    return BestI, minNeighbors     

endpoints=open('f0MipEndpoints.pckle','rb')
crds=cPickle.load(endpoints)
length=len(crds)
print 'length',  length #gives number of endpoints labeled
#img = io.readImage(str(sys.argv[2]),returnITK=False,imgMode="uchar")
img = io.readImage('PE00026Filter0_seg.mha',returnITK=False,imgMode="uchar")
mask = na.where(img>0,1,0) 
point=nxvasc.nxvasc()
fle=open("Modifiedf0MipEndpoints5x5.pckle",'wb')
point.setMask(mask) 
point.createMaskDictionary()
"""We first map the crds back to the index of the potential endpoints location
within the image using getInds from nxvasc.py"""
ind=point.getInds(crds) #maps crds to inds and returns inds a (list of indicies)
#to be passed to getValidNeighbors.
point.get5x5matrix() #need to define self.d26 for getNeighbors, defines
#relationship between the neighbors
count=0 #keep track of the number of replacements to be made
for ic in range(len(ind)):
    print "ic",  ic 
    i=ind[ic] #i is the index at the icth location
    print "i",  i # check
    #maskNeighbors stores the crds of all pts. w/in the neighbors
    #of i that lie within the mask.
    maskNeighbors=point.getValidNeighborsInformation(i) 
    newi = grabBestEndpoint(maskNeighbors[0],point)
    #if the new pt. has fewer neighbors than the original pt.
    if newi[1]<len(maskNeighbors[0]): 
        p=point.get_crds(point.inds[newi[0]]) #get the new pts crds.
        #replace the original pt. with the new pt.
        crds[ic][0] =  p[0] ; crds[ic][1] = p[1]; crds[ic][2]=p[2] 
        count +=1 #increase count by 1, made a replacement
        print "replaced %d (%d) with %d (%d)"%(i,len(maskNeighbors[0]),ind[ic],newi[1])
cPickle.dump(crds,fle) #output the new crds into a new file



    

