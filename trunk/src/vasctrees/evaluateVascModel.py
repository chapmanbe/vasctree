#!/usr/bin/env python
import networkx as nx
import numpy as np
import sys
import cPickle
import imageTools.ITKUtils.io as io
import os
import imageTools.browse.a3d as a3d
import itk
import subprocess
from SkeletonGraph import *

def main():
    #oimg = io.readImage(sys.argv[1],returnITK=False,imgMode = "sshort")
    oimg = io.readImage("PE00009.mha",returnITK=False,imgMode = "sshort")
    #tmp = os.path.splitext(sys.argv[1])
    tmp = os.path.splitext("PE00009.mha")
    pfile = tmp[0]+"greatOrigins.pckle"
    a3d.call(data=[oimg], title="label pulmonary trunks",
             labels=["leftPulmonaryTrunk","rightPulmonaryTrunk"],colors=["red","blue"],
             AllowAddPoints=True, pointsFile=pfile, AllowDeletePoints=True)
    origins = cPickle.load(open(tmp[0]+"greatOrigins.pckle",'rb'))
    #reader = itk.ImageFileReader.IUC3.New(FileName=sys.argv[2])
    reader = itk.ImageFileReader.IUC3.New(FileName="PE00009Filter0_seg.mha")
    
    filler = itk.VotingBinaryIterativeHoleFillingImageFilter.IUC3.New()
    filler.SetInput(reader.GetOutput())
    
    #tmp2 = os.path.splitext(sys.argv[2])
    tmp2 = os.path.splitext("PE00009Filter0_seg.mha")
    outFill = tmp2[0]+"_fill.mha"
    outSkel = tmp2[0]+"_fill_skel.mha"
    writer = itk.ImageFileWriter.IUC3.New()
    writer.SetInput(filler.GetOutput())
    writer.SetFileName(outFill)
    print "filling in holes in segmentation"
    writer.Update()
    subprocess.call("BinaryThinning3D %s %s"%(outFill,outSkel),shell=True)
    print "Generating Skeleton"
    img = io.readImage(outSkel,returnITK=False,imgMode = "uchar")
    sg = SkeletonGraph(img) 
    print "generating graph from skeleton"
    sg.getGraphFromSkeleton() #generates graphs
    for i in range(len(sg.graphs)): #loop through stored graphs
        print "processing graph %d"%i 
        sg.setCurrentNumber(i) #graph count
        sg.setCurrentGraph()
        sg.findEndpointsBifurcations() #identify endpoints and bifurcation points and stores as class attributes
    fo = open(pfile,'rb')
    origins = cPickle.load(fo)
    sg.setRoots(origins)#determine where to traceback to, the point on the pulmonary trunk
    print "ordering graphs" #need to point the paths in the correct order, have the root and the endpoints
    for i in range(len(sg.graphs)):  
        sg.setCurrentNumber(i)
        sg.traceEndpoints() #traceback paths      
    
    sg.saveGraphs(tmp2[0]+"_graphs.pckle") #save the resulting ordered graph
if __name__ == '__main__':
    main()