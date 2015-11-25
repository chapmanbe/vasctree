#GenerateGraphs.py
"""The goal is to generate th NXGraph and pickle the output """
import sys
sys.path.append("../../vasctrees")
import imageTools.ITKUtils.io as io
import os
import VascSegment
from RelatedPoints import *
import VascMask
import time
import cPickle
import numpy as na

def GenerateGraph():
    graph=open("PE00025CompleteNXGraph.pckle", "wb") #stores the graph
    img=io.readImage("PE00025Filter0_seg.mha",returnITK=False,imgMode="uchar")
    print "image loaded"
    mask = na.where(img>0, 1, 0)
    print "mask created"
    instance=VascMask.VascMask()
    print "class instance generated"
    instance.setMask(mask)
    print "mask set"
    instance.setNeighborhoodSize(sz=3)
    print "Neighborhood gathered"
    instance.getFOM()
    print "FOM obtained"
    instance.createNXGraph()
    cPickle.dump(instance.G, graph)
if __name__=='__main__':
    GenerateGraph()
    
    
