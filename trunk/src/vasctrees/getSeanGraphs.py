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
from optparse import OptionParser

from SkeletonGraph import SkeletonGraph

def getParser():
    try:
        
        usage = """This program reads in a skeleton image stored in a standard 3D image format (e.g. meta image). """+\
                """The program will first check to see if the image is compressed in a gnuzip format and will uncompress it if necessary. """+\
                """The program also needs an origin file that will be used to set the origins for the graphs. """+\
                """Currently the origins need to be stored in a Pickle file and be in the CritPoint format. """+\
                """For each specified origin, the program will order the created graph based on that origin. """+\
                """Thus the graphs are duplicated for each origin."""
        parser = OptionParser(usage=usage)
        parser.add_option("-i", "--img", dest="filename", help="binary image to read and threshold", default=".dcm")
        parser.add_option("-o", "--origins", dest="originsFile", help="file containing the arterial and venous origins for this subject",
                          default="")
        parser.add_option("-n", "--numIter", dest="iterations",type="int",default=10)

        return parser
    except Exception,  error:
        print "failed to generate parser",  error
        


def main():
    try:
        parser = getParser()
        (options, args) = parser.parse_args()
        successfullUncompress = subprocess.call("gunzip %s"%(options.filename+".gz"),shell=True)
        img = io.readImage(options.filename,returnITK=True,imgMode = "uchar")
        sg = SkeletonGraph(img)
        print "generating graph from skeleton"
        sg.getGraphsFromSkeleton()

        for i in range(len(sg.graphs)):
            print "processing graph %d"%i
            sg.setCurrentGraph(i)
            sg.findEndpointsBifurcations()
            
        sg.setLargestGraphToCurrentGraph()    
        ofile = file(options.originsFile,'rb')
        originCrds = cPickle.load(ofile)
        for o in originCrds:
            #originInds = np.unravel_index(o,img.shape)
            oint = (int(o[0]+0.5),int(0.5+o[1]),int(0.5+o[2]))
            print "tracing graph for origin",oint
            sg.setRoot(oint, key=o.getProperty("id"))
            sg.traceEndpoints(key=o.getProperty("id"))
      
        print "save the graphs"
        tmp2 = os.path.splitext(options.filename)
        sg.saveGraphs(tmp2[0]+"_graphs.pckle")
        if( not successfullUncompress ):
            print "compress the image"
            subprocess.call("gzip %s"%(options.filename),shell=True)
    except Exception, error:
        print "failed in getSeanGraphs due to error:",error
    

if __name__ == '__main__':
    main()
