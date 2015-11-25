"""The goal is to generate th NXGraph and pickle the output and to generate the paths using dijkstra.py and pickle the output
2 output files will be generated so that they do not have to be created everytime while working on generating
better pruning rules"""

import sys
sys.path.append("../../vasctrees")
import imageTools.ITKUtils.io as io
import os
import VascSegment
from RelatedPoints import *
import VascMask
import time
import pickle
import numpy as na

def GenerateNonEndpointPaths():
    graph=open("PE000026NENXGraph.pckle", "wb") #stores the graph
    #paths=open("PE00026Paths.pckle", "wb") #stores the paths
   #indexes=open("Indexes.pckle", "wb") #stores the index locations for each set of crds.
    endpoints=open("PE00026Nonendpoints.pckle", 'rb')
    inds=pickle.load(endpoints)
    img=io.readImage("PE000026Filter0_seg.mha",  returnITK=False,  imgMode="uchar")
    mask = na.where(img>0, 1, 0)
    instance=VascMask.VascMask()
    instance.setMask(mask)
    instance.setNeighborhoodSize(sz=3)
    instance.getFOM()
    #inds=instance.getInds(crds)
    instance.createNXGraph()
    pickle.dump(inds, indexes)
    pickle.dump(instance.G, graph)
if __name__=='__main__':
    GeneratePaths()
    
    
