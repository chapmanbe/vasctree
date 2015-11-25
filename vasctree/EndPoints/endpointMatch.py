import os 
import sys
#Must include the path to nxvasc and its components
#sys.path.append("../../../VascTrees/trunk/src/vasctrees")
sys.path.append("../../vasctrees")
import nxvasc
import dicom
import pickle
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
    minNeighbors=30 #never have a point with 30 neighbors in 26 pt. nborhood
    BestI=-1 # never have a point that has no neighbors
    for i in neighbors:#get the neighbors that are in the mask
        data=point.getValidNeighborsInformation(point.inds[i]) 
        if len(data[0])< minNeighbors: 
            BestI=i
            #new best point with minneighbors as the total number of neighbors
            minNeighbors=len(data[0])
            #returns the number of neighbors in the mask
    return BestI, minNeighbors     

# we need to read in pickle file and image
#endpoints=open(sys.argv[1],'r')
#contains the x,y,z coordinates for each potential endpoint
endpoints=open('f0MipEndpoints.pckle','rb') #replaces commented out line above
crds=pickle.load(endpoints)
length=len(crds)
print('length',  length) #gives number of endpoints labeled
#img = io.readImage(str(sys.argv[2]),returnITK=False,imgMode="uchar")
img = io.readImage('PE00026Filter0_seg.mha',returnITK=False,imgMode="uchar")
#create the mask, binary system 1 if part of the image 0 if not
mask = na.where(img>0,1,0) 

point=nxvasc.nxvasc() #create an instance of the class
fle=open("Modifiedf0MipEndpoints.pckle",'wb') #Output file
point.setMask(mask) #Set the mask using the numpy image mask. In addition to
#reading the mask, the 1D indicies into the 3D image are generate and stored

point.createMaskDictionary()#Create dictionary that maps the index into the 3D
#volume to an index into the mask. The 1D array into the 3D volume is the key &
#the ordinal position of the index is the value

"""We first map the crds back to the index of the potential endpoints location
within the image using getInds from nxvasc.py"""

ind=point.getInds(crds) #maps crds to inds and returns inds a (list of indicies)
#to be passed to getValidNeighbors.

#print "indexes for selected endpoints are:",ind
#ex. using tree2.dcm [3337483, 3394677, 3501459, 3284815, 3519599] 
#print "ind", ind #check

point.get3x3matrix() #need to define self.d26 for getNeighbors, defines
#relationship between the neighbors

count=0 #keep track of the number of replacements to be made
for ic in range(len(ind)):
    print("ic",  ic) #position in the list iue. the first is 0, then 1, 2 ect.
    i=ind[ic] #i is the index at the icth location
    #print "i",  i # check
    #maskNeighbors stores the crds of all pts. w/in the 26 neighbors
    #of i that lie within the mask.
    maskNeighbors=point.getValidNeighborsInformation(i) 
    newi = grabBestEndpoint(maskNeighbors[0],point)
    #if the new pt. has fewer neighbors than the original pt.
    if newi[1]<len(maskNeighbors[0]): 
        p=point.get_crds(point.inds[newi[0]]) #get the new pts crds.
        #replace the original pt. with the new pt.
        crds[ic][0] =  p[0] ; crds[ic][1] = p[1]; crds[ic][2]=p[2] 
        count +=1 #increase count by 1, made a replacement
        print("replaced %d (%d) with %d (%d)"%(i,len(maskNeighbors[0]),ind[ic],newi[1]))
pickle.dump(crds,fle) #output the new crds into a new file



    

