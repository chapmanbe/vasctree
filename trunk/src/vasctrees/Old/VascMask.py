"""
***********
class definitions for extracting a vascular tree structure from a segmentation.

This is a modification begun in December 2008 to code most recently modified
December 2006. The code I am modifying from is defined in bdv9.py

Initial efforts will be placed in updating the code to be dependent on the most recent python
libraries (e.g. replacing na and numarray with numpy)

I will then work on continuing to separate out graphics and display from computation
"""
# Split off from bdv4 02/02/2005
# My plan is to make this into a more ordered entity by keeping
# A list of trees rather than lumping all the disconnected groups 
# into a single tree
# bdv5 12/22/2004 Major rewrite to incoporate multiple discontiguous regions
# bdv5 02/02/2005 I have tried to remove all functions not related to the
# Dijkstra cost function and Dijkstra tracing.
# 2/16/2005 I need to use na instead of numarray. Speed is killing me.
# 7/19/2005 modbifying bdv5 to bdv6. I need to break up the computing of voxel neighborhood
# maps so that I am only generating maps for the current contiguous segment I am processing
# 11/17/2005 I am breaking up the graphic and computation portions of this
# code. I will create an inherited class which will contain the graphics
# 12/20/2006 Reworking on Mac. Getting rid of tabs so that Textwrangler works correctly

import networkx as nx
#import imageTools.ITKUtils.io as io
import dicom
import os
import numpy as na
import scipy.ndimage as ndi
import math
import cPickle
import sys

import string
import VascSegment
from RelatedPoints import *
#from Path import *
from NewPaths import *
import matplotlib.pyplot as plt 
import pylab
import time
from scipy import weave
import matplotlib.pyplot as pyplot
import pp

class VascMask(object):
    """Basic class for processing and anayzing a vascular structure"""
    # define initialization routine
    def __init__(self):
        """Constructor for VascTree class.
        description
        """

        self.cf = None
    
        #self.fomf = self.fomf3
        self.fom = None
        self.dim = None
        self.vmap = None
        self.G = nx.Graph()
        self.edges = []
    def setNeighborhoodSize(self,sz=3):
        """define the neighborhood size to use for connection calculations"""
        self.sz = 3
        dsz = int(sz/2)
        self.dist = na.zeros((sz,sz,sz))
        for k in range(-dsz,dsz+1):
            for j in range(-dsz,dsz+1):
                for i in range(-dsz,dsz+1):
                    self.dist[k,j,i] = math.sqrt(k**2+j**2+i**2)
    def findSeed(self):
        if( self.fom == None ):
            self.getFOM()
        ind = self.fom.argmin()
        return self.mask.flat[ind]
        
    def getSurfacePoints(self):
        inds =  na.nonzero(self.fom.flat == -1)[0]
        return self.mask.flat[inds]
    
            
    def getFOM(self):
        """This function takes the mask file associated with self and computes
    a distance from edge map using scipy.ndimage.distance_transform_cdt.
    
    The resulting distance map is assigned to a rawFigureOfMerit attribute of self"""
        self.fom = ndi.distance_transform_cdt(na.where(self.mask>0,1,0))
        self.fom = self.fom.max()-self.fom
        #self.rawFigureOfMerit = dfe.take(self.inds)
    def setCostFunction(self,func): #cost function
        """set the object cost function to be equal to the func referenced in
        func"""
        self.cf = func
    def setMask(self, mask):
        """Set the mask using the numpy image mask. In addition to reading the
    mask, the 1D indicies into the 3D image are generate and stored"""
        inds = na.nonzero(mask.flat)[0]
        self.dim = mask.shape[::-1]
        self.mask = na.zeros(mask.shape,na.uint32)
        self.mask.put(inds,inds)
        self.inds = inds

    def getMask(self):
        """return the mask file associated with the object"""
        return self.mask

    def getCrds(self,ind):
        """Given an array of 1D indicies into the image, return an Nx3 ??? array of the x,y,z coordinates"""
        ind = na.array(ind)
        nx = self.dim[0]
        ny = self.dim[1]
        nxny = self.dim[0]*self.dim[1]
        crd = na.transpose(na.array([ (ind % nx), \
                                      (ind / nx)%ny,\
                                       ind / nxny]))
        return crd
        
        def getInds(self,crds): #added from nxvasc 3-5-10 to convert crds to inds for NXGraph
            """given the x,y,z coordinates return the corresponding 1D index data can be passed in 
            either as a sequence of x,y,z crds or x, y, z can be passed in separately"""
        try:
            ind = []
            for crd in crds:
                ind.append(crd[0]+crd[1]*self.dim[0]+crd[2]*self.dim[0]*self.dim[1])
            return ind
        except:
            return None 
        
        
    def getNeighborhoodInfo(self, start, end): #distances = False,coordinates=False,figuresOfMerit=False ):
        """ get the coordinates of all points within the 26-point neighborhood
        of index that lie within the mask.
    
        The function returns the indicies into the the 3D image by default and the following
        values are returned optionally, depending on how the flag values are set
        
        distances: The step distances between p and each of its valid neighbors
        coordinates: The (x,y,z) coordinates for each valid neighbor
        figureOfMerit: The point figure-of-merit for each valid neighbor
        
        """
        new_pnts = self.mask[start[2]:end[2],start[1]:end[1],start[0]:end[0]]
        inds = na.nonzero(new_pnts.flat)[0]
        pnts = na.take(new_pnts.flat,inds)
        return pnts, self.fom.flat[pnts], self.dist.flat[inds]
        
    def createNXGraph( self ):
        """create a networkx graph that represents the relationship between each point in the currently labeled
    mask and each of its 26-point neighbors"""

        linds = len(self.inds)
        
        
        crds = self.getCrds(self.inds)
        starts = na.maximum(crds-1,0)
        ends = na.minimum(crds+2,self.dim)
        edges = []

        for i in xrange(len(self.inds)):
            start = starts[i]
            end = ends[i]
            new_pnts = self.mask[start[2]:end[2],start[1]:end[1],start[0]:end[0]]
            inds = na.nonzero(new_pnts.flat)[0]
            neighbors = na.take(new_pnts.flat,inds)
            fom = self.fom.flat[neighbors]
            dist = self.dist.flat[inds]
            edgeCosts = fom*dist
            edges.extend([(self.inds[i],neighbors[j],{'weight':edgeCosts[j]}) for j in range(len(neighbors))])
        self.G.add_edges_from(edges)
    
    def createMaskDictionary(self,  inds): #Added 3-7-10, probably better way to do this, but using for now for AMIA paper
        """Create dictionary that maps the index into the 3D volume to an index into the mask
    The 1D array into the 3D volume is the key of the dictionary.
    The ordinal position of the index is the value """
        try:
            self.maskMap = dict(zip(inds,range(len(inds))))
            #self.maskSet = set(self.inds)
        except Exception, error:
            print "failed in createMaskDictionary", error    
            
    def getGraphTarget( self ):
        """look at the nodes of G (points within a labeled structure) and select 
    node within graph that has the maximum raw figure-of-merit value (by
    default, distance from edge)"""
        try:
            nodes = na.array(self.G.nodes())
            print nodes.max(), nodes.min()
            vals = na.take(self.fom,nodes)
            maxind = vals.argmax()
            return nodes[maxind]
        except Exception, error:
            print "failed in getGraphTarget()", error
            
    def GenerateAstarPaths(self, inds, G,   verbose=False): #Added 3-6-10
        """employs the a star search algorithm to find the shortest paths between detected endpoints and the seed"""
        try:
            self.termInds=inds
            if(verbose):
                print "Identify A star paths"
                seed=self.getGraphTarget() #NEED TO ADD IN ALSO
                self.seed=seed
                self.paths={}
                maxPath=-1
                maxPathNode=None
                count=0
                tempP=nx.floyd_warshall(G)
                for ind in self.termInds:
                    node=self.maskMap[ind] #Need to check this call, added
                    self.paths[node]=nx.astar_path(G,  node,  seed)
                    print  "Processed %d of %d endpoints"%(len(self.paths), len(self.termInds))
                    if(maxPath<len(self.path[node])):
                        maxPath=len(self.path[node])
                        maxPath=node
                print maxPathNode,  maxPath
                self.maxPathNode=maxPathNode
                self.maxPath=maxPath
        except Exception,  error:
            print "failed in a star paths",  error
            
                    
                
        
        
        
    def createNXGraphPP(self, chunk=4):
        import pp
        ppservers = ()
        job_server = pp.Server(ppservers=ppservers)
        print "Starting pp with", job_server.get_ncpus(), "workers"
        
        linds = len(self.inds)
        chunkSize = int(linds/chunk)
        
        crds = self.getCrds(self.inds)
        starts = na.maximum(crds-1,0)
        ends = na.minimum(crds+2,self.dim)
        
        s = 0
        e = s+chunkSize
        rslt = []
        for j in range(chunk):
            inds_chunk = self.inds[s:e]
            starts_chunk = starts[s:e]
            ends_chunk = ends[s:e]
            s = e
            e = min(linds,e + s)
            r = job_server.submit(self.getGraphEdges, (inds_chunk, starts_chunk, ends_chunk),
                              depfuncs = (self.getNeighborhoodInfo, self.cf) )
            rslt.append(r)

        job_server.wait()
        edges = []
        for r in rslt:
            print type(r)
            edges.extend(r())
    def getGraphEdges(self,inds, starts, ends):
        edges = []
        for i in xrange(len(inds)):
            neighbors, fom, dist = self.getNeighborhoodInfo(starts[i], ends[i])
            edgeCosts = self.cf(fom, dist,0)
            edges.extend( [(self.inds[i],neighbors[j],{'weight':edgeCosts[j]}) for j in range(len(neighbors))] )
        return edges
    def collectEdges(self, newEdges):
        self.edges.extend(newEdges)
    def getValidIndicies(self, points):
        """...
        What we want here is the indicies into points for members of points that are within the mask
    
        """
        try:
            inds = [ i for i in range(points.size) if points.flat[i] in self.maskSet ]
            return inds
        except Exception, error:
            print "failed in getValidIndicies", error
            return -1

    def getMaskMips(self):
        """get the orthogonal (x,y,z) MIPS of the mask.
        Also compute the depth buffers for each MIP"""
        try:
            self.zmip = self.mask.max(axis=0)
            self.zbuffer = self.mask.argmax(axis=0)

            self.ymip = self.mask.max(axis=1)
            self.ybuffer = self.mask.argmax(axis=1)

            self.xmip = self.mask.max(axis=2)
            self.xbuffer = self.mask.argmax(axis=2)
        except Exception, error:
            print "failed in getMaskMips", error

