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
import imageTools.ITKUtils.io as io
import dicom
import os
import numpy as na
import scipy.ndimage as ndi
import math
import pickle
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

class nxvasc(object):
    """Basic class for processing and anayzing a vascular structure"""
    # define initialization routine
    def __init__(self):
        """Constructor for VascTree class.
        description
        """

        # initialize filenames
        self.vsuffix = "_vt"
        self.fomFile = None
        self.outputFile = None

        # set up lists and dictionaries
        self.rawFigureOfMerit = None 
        self.mask = None
        self.paths = []
        self.fpaths = []
        self.ftrees = {}
        self.tree = {}
        self.bifurcations = {}
        self.G = {}
        self.maskMap = {}
        self.maskSet = None 
        # variable functions
        # book keeping variables
        self.__minPathLength = 5
        # cost function parameters
        self.cf = None
    
        #self.fomf = self.fomf3
        self.fomf = None
        self.dim = None
        self.vmap = None
        self.get3x3matrix()
#        self.get5x5matrix() #NEW 2-16-10AM
#        self.get7x7matrix() #NEW 2-17-10AM

    def get3x3matrix(self): #copied over from VascTree program, 10-6-09
        """define the 3x3 neighborhood relationship matrix"""
        try:
            i = na.identity(3)
            self.d26 = i.copy()
            self.ds26 = na.zeros(26,na.float64)
        
            for k in range(1,26):
                self.d26 = na.concatenate((self.d26,i))
            count = 0
            a = []
            for k in range(-1,2,1):
                for j in range(-1,2,1):
                    for i in range(-1,2,1):
                        if( i != 0 or j != 0 or k != 0 ):
                            self.ds26[count] = math.sqrt(i**2+j**2+k**2)
                            count += 1
                            a.append(i)
                            a.append(j)
                            a.append(k)
            a = na.reshape(na.array(a),(78,1))
            self.d26 = na.concatenate((self.d26,a),axis=1)
        except Exception as error:
            print("failed in get3x3matrix(): ", error)
            
    def get5x5matrix(self): #ADDED 2-16-2010AM
        """define the 5x5 neighborhood relationship matrix"""
        try:
            i = na.identity(3)
            self.d124 = i.copy()
            self.ds124 = na.zeros(124,na.float64)
        
            for k in range(1,124):
                self.d124 = na.concatenate((self.d124,i))
#            print len(self.d124)
            count = 0
            a = []
            for k in range(-2,3):
                for j in range(-2,3):
                    for i in range(-2,3):
                        if( i != 0 or j != 0 or k != 0 ):
                            self.ds124[count] = math.sqrt(i**2+j**2+k**2)
                            count += 1
                            a.append(i)
                            a.append(j)
                            a.append(k)
#            print len(a)
            a = na.reshape(na.array(a),(372,1))
#            print len(self.d124)
            self.d124 = na.concatenate((self.d124,a),axis=1)
        except Exception as error:
            print("failed in get5x5matrix(): ", error)
    def get7x7matrix(self): #ADDED 2-17-2010AM
        """define the 7x7 neighborhood relationship matrix"""
        try:
            i = na.identity(3)
            self.d342 = i.copy()
            self.ds342 = na.zeros(342,na.float64)
            for k in range(1,342):
                self.d342 = na.concatenate((self.d342,i))
            count = 0
            a = []
            for k in range(-3,4):
                for j in range(-3,4):
                    for i in range(-3,4):
                        if( i != 0 or j != 0 or k != 0 ):
                            self.ds342[count] = math.sqrt(i**2+j**2+k**2)
                            count += 1
                            a.append(i)
                            a.append(j)
                            a.append(k)
            a = na.reshape(na.array(a),(1026,1))
            self.d342 = na.concatenate((self.d342,a),axis=1)
            #print "d342",  self.d342
        except Exception as error:
            print("failed in get7x7matrix(): ", error)
            
    def setCostFunction(self,func): #cost function
        """set the object cost function to be equal to the func referenced in
        func"""
        self.cf = func
    def setFigureOfMeritF(self,func):#figure of merit function
        self.fomf = func
    def setMinPathLength(self,mpl):#determines how short a path can be to be considered a path
        """set the minimum number of voxels that constitute a path"""
        self.__minPathLength = mpl
    def getMinPathLength(self):
        """return the minimum number of voxels that constitute a path"""
        return self.__minPathLength
    def setOutputFile(self, maskFile):
        """Sets object mask to image located in maskFile"""
        self.outputFile = maskFile
    def getOutputFile(self):
        return self.outputFile
       
    def createValsAndSources(self):
        """Create ones and zeros arrays to store vals and newsources 
        """
        try:
            self.vals = na.ones(len(self.inds),na.float32)
            self.newsources = na.zeros(len(self.inds),na.int32)
        except Exception as error:
            print("failed in createValues", error)
    def createMaskDictionary(self):
        """Create dictionary that maps the index into the 3D volume to an index into the mask
    The 1D array into the 3D volume is the key of the dictionary.
    The ordinal position of the index is the value """
        try:
            self.maskMap = dict(list(zip(self.inds,list(range(len(self.inds))))))
            self.maskSet = set(self.inds)
        except Exception as error:
            print("failed in createMaskDictionary", error)
    def setFigureOfMeritfile(self, fomFile):
        """Sets object figure of merit image to data in fomFile"""
        self.fomFile = fomFile
    def getFigureOfMeritfile(self):
        return self.fomFile
    def getRawFigureOfMerit(self):
        return self.rawFigureOfMerit
    def fillFigureOfMerit(self):
        """Generate the fom data from the objects figure-of-merit function (fomf)"""
        try:
            self.fom = self.fomf(*(self.rawFigureOfMerit,))
        except Exception as error:
            print("failed in fillFigureOfMerit", error)
    def generateRawFigureOfMeritData(self):
        """This function takes the mask file associated with self and computes
    a distance from edge map using scipy.ndimage.distance_transform_cdt.
    
    The resulting distance map is assigned to a rawFigureOfMerit attribute of self"""
        try:
            dfe = ndi.distance_transform_cdt(self.mask)
            self.rawFigureOfMerit = dfe.take(self.inds)
        except Exception as error:
            print("failed in generateRawFigureOfMeritData", error)
    def setMask(self, mask):
        """Set the mask using the numpy image mask. In addition to reading the
    mask, the 1D indicies into the 3D image are generate and stored"""
        try:
            self.mask = mask
            self.inds = na.nonzero(self.mask.flat)[0]
            print("length of self.inds",len(self.inds))
            print(self.inds)
            self.dim = self.mask.shape[::-1]
            print(self.mask.shape)
            return True
        except Exception as error:
            print("failed in setMask", error)
    def getMask(self):
        """return the mask file associated with the object"""
        return self.mask

    """Replace the proliferation of cf (cost function) methods with a method that calls 
       a cost function from a library passing the relevant class attributes as function
       arguments"""
 
    """Replace the proliferation of fom (figure of merit) methods with a method that generates 
       a cost function from a library passing the relevant class attributes as function
       arguments"""
    def getMaxDFEValues(self):
        """either reads from disk precomputed MaxDFE values or computes them.
        I need to add a test to see if they already exist in the object
    
    MaxDFE is th maximum distance from edge. Need to explain better what this means.
    
    I also need to write the function that is called if the read fails
    """
        if( not self.readMaxDFEValues() ):
            pass

            
    def findSeedSegment(self, s=0, loc=-1):
        """find which segment(s) has(have) the sth seed point at the loc element. We assume that the seed point is at
    either the last (loc=-1) position in the list or the first (loc=0)"""
        try:
            sind = self.seeds[s]
            matchs = []
            for i in range(len(self.paths)):
                ind = self.paths[i][loc]
                if( ind == sind ):
                    matchs.append(i)
            return matchs
        except Exception as error:
            print("failed in findSeedSegment()",error)
    def findSegmentChildren(self, segNum,s=-1,loc=0):
        """find segment indicies which are children of the segment indexed by segNum
        segNum: an index into self.paths
        s: location of the segNum path to test for children (-1 or 0)
        loc: location of the child path to test for children (-1 or 0)
        
        ???Should there be a forced relationship between s and loc???
        """
        try:
            # get the end point of the parent (segNum) segment
            parentEndPoint = (self.paths[segNum])[s]
            children = []
            for i in range(len(self.paths)):
        # don't match a segment with itself
                if( i != segNum ):
                    # get the beginning point of the ith segment
                    childBeginPoint = (self.paths[i])[loc]
                    if( childBeginPoint == parentEndPoint ):
                        children.append(i)
                    elif( parentEndPoint in self.paths[i] ):
            # this is some kind of error state
                        print("points do not match at ends but point is common to both paths")
            return children
        except Exception as error:
            print("failed in findSegmentChildren()",error)
    
    def save_voxel_map(self, suffix="_vm.pckle", save_mode = 1):
        """write the voxel map to a cPickle file.
    
    read_mode= 1 (or any boolean True value) opens the file in a binary mode
    read_mode= 0 (or any boolean False value) opens the file in a non-binary mode"""    
        try:
            if( save_mode):
                omode = "wb"
            else:
                omode = "w"
            fo = open(self.outputFile+self.vsuffix+suffix,omode)
            pickle.dump([self.map_inds,self.vmap],fo,save_mode)
            fo.close()
        except Exception as error:
            print("failed in save_voxel_map()",error)
            sys.exit()

    def estimateVesselSizesFromMap(self):
        """Does a real basic shape estimate from the voxel mapping for each vessel segment
    The function uses matplotlib to generate a png file 
    """
        tkeys = list(self.trees.keys())
        lengths = []
        radii = []
        for tkey in tkeys:
            tree = self.trees[tkey]
            keys = list(tree.keys())
            maxseg = na.max(self.vmap)+1
            for key in keys:
                seg = tree[key]
                path = self.paths[seg.segmentNumber]
                ind = na.nonzero(self.vmap == seg.segmentNumber )[0]
                lengths.append(len(path))
                r = math.sqrt(len(ind)/(math.pi*len(path)))
                radii.append(r)
                print("segment ",seg.segmentNumber," volume (voxels): ",len(ind)," length: ",len(path)," estimated radius: ",r)
        lengths = na.array(lengths)
        radii = na.array(radii)
        plt.plot(lengths,radii)
        plt.xlabel("Segment Length")
        plt.ylabel("Segment Radius")
        plt.savefig(self.outputFile+"_length_radius.png")
        return lengths, radii
    def showPaths(self, paths,label=''):

        maskz = self.zmip.copy()
        masky = self.ymip.copy()
        maskx = self.xmip.copy()

        plt.clf()
        plt.gray()
        colors = ['r','g','b','y','p']
        nc = len(colors)
        for i in range(len(paths)):
            p = paths[i]
            try:
                imgInds = na.take(self.inds,list(p))
                crds = self.get_crds(imgInds)
                maskz[crds[:,1],crds[:,0]] += 1
                masky[crds[:,2],crds[:,0]] += 1
                maskx[crds[:,2],crds[:,1]] += 1
            except:
                pass

        print(maskz.max())
        pyplot.subplot(221)
        pyplot.imshow(maskz)
        pyplot.subplot(222)
        pyplot.imshow(masky)
        pyplot.subplot(223)
        pyplot.imshow(maskx)

        plt.gray()
        plt.savefig(label.replace(' ','')+".png")
        plt.show()
        #fname = label.replace(' ','')+".pckle"
        #fo = open(fname,'wb')
        #cPickle.dump([maskz,masky,maskx,paths],fo)
        #fo.close()

    def plotPaths(self, paths,label='', show=False):
        """A quick and dirty plotting of the centerlines using pylab"""
        plt.clf()
        colors = ['r','g','b','y','p']
        nc = len(colors)
        for i in range(len(paths)):
            p = paths[i]
            try:
                imgInds = na.take(self.inds,list(p))
                crds = self.get_crds(imgInds)
                plt.plot(crds[:,0],crds[:,1],"%s"%colors[i%nc])
                                  
            except:
                pass

        plt.title(label)
        plt.xlim(0,32)
        plt.ylim(0,32)
        plt.savefig(label.replace(' ','')+".png")
        if( show ):
            plt.show()
    def mapVoxels( self, maxvalue=1e16, verbose=False ):
        """
        Take the list of points with values (what are values?) less than maxvalue and map 
        them to specific segments (paths)
    
    If verbose is True, periodic progress updates are printed
        """
        try:
            # find list of points which have a valid cost function value
            inds = na.nonzero( self.vals < maxvalue )[0]
            self.map_inds = RelatedPoints(na.take(self.inds,inds),size=self.dim) # need to set sizes
        
        # points will be an Nx3 array. The second dimension corresponds to the x,y,z coordinates
            points = self.map_inds.getCrds()
        
        # self.vmap will be an N-dimensional vector with N equal to the number of voxels satisfying
        # the inclusion criteria
        
        # Can I replace the for loop with a more vectorish approach that is more efficient?
        # Or maybe I need to use pysco or something similar
        
        # the nested for loop is finding which path has the minimum distance to each point
            self.vmap = na.zeros((len(self.map_inds)),na.int16)
            for i in range(points.shape[0]):
                if( verbose and i % 1000 == 0 ):
                    print("processing point ", i, " of ", points.shape[0])
                p = points[i,:]
                mindist = 1e16
                mp = 0
                for k in range(len(self.paths)):
                    pth = self.paths[k]
                    pth.computeCrds()
                    d = pth.getMinimumDistance2(p)
                    if( d < mindist ):
                        mindist = d
                        mp = k
                self.vmap[i] = mp
        except Exception as error:
            print("Failed in mapVoxels() ",error)
        

    def fit_ordered_paths(self,maxiter=5):
        """loop through all the ordered paths and fit a least squares (smoothing spline) to the centerline"""
        try:
            for tkey in list(self.trees.keys()):
                tree = self.trees[tkey]
                keys = list(tree.keys()) 
                ftree = {}
                for key in keys:
                    seg = tree[key]
                    data = self.fit_path(self.paths[seg.segmentNumber],maxiter)
                    ftree[key] = data
                    self.ftrees[tkey] = ftree
            
        except Exception as error:
            print("failed in fit_ordered_paths()",error)
            sys.exit()
    def save_fit_paths(self, suffix="_fpaths.pckle", save_mode = 1):
        """Save the least-squares smoothed spline fits of the centerlines to a
    cPickle file. save_mode=True uses a binary file format"""
        try:
            if( save_mode):
                omode = "wb"
            else:
                omode = "w"
            fo = open(self.outputFile+self.vsuffix+suffix,omode)
            pickle.dump([self.fpaths,self.paths,self.ftrees],fo,save_mode)
            fo.close()
        except Exception as error:
            print("failed in save_fit_paths()",error)
            sys.exit()

    def save_path_data(self,suffix="_rpaths.pckle", save_mode=1):
        """save the path data into a cPickle file. save_mode=True saves the file in a binary format"""
        try:
            if( save_mode):
                omode = "wb"
            else:
                omode = "w"
            fo = open(self.outputFile+self.vsuffix+suffix,omode)
            pickle.dump([self.paths,self.visited,self.trees,self.terminals],fo,save_mode)
            fo.close()
        except Exception as error:
            print("failed in save_path_data()",error)
            sys.exit()



    def get_crds(self,ind):
        """Given an array of 1D indicies into the image, return an Nx3 ??? array of the x,y,z coordinates"""
        try:
            ind = na.array(ind)
            nx = self.dim[0]
            ny = self.dim[1]
            nxny = self.dim[0]*self.dim[1]
            crd = na.transpose(na.array([ (ind % nx), \
                                          (ind / nx)%ny,\
                                           ind / nxny]))
            return crd
        except Exception as error:
            print("failed in get_crds ", error)
            return -1


    def getValidNeighborsInformation(self, index, distances = False,coordinates=False,figuresOfMerit=False ):
        """ get the coordinates of all points within the 26-point neighborhood
        of index that lie within the mask.
    
    The function returns the indicies into the the 3D image by default and the following
    values are returned optionally, depending on how the flag values are set
    
    distances: The step distances between p and each of its valid neighbors
    coordinates: The (x,y,z) coordinates for each valid neighbor
    figureOfMerit: The point figure-of-merit for each valid neighbor
    
    """
        try:
            p = self.get_crds(index)
            new_pnts = na.reshape(\
                    na.inner(self.d26,\
                    na.array([p[0],p[1],p[2],1])),\
                             (26,3))
            cx = new_pnts[:,0]
            cy = new_pnts[:,1]
            cz = new_pnts[:,2]
            ind = na.nonzero((cx >=0 )*( cx < self.dim[0])*\
                             (cy >=0 )*( cy < self.dim[1])*\
                             (cz >=0 )*( cz < self.dim[2]))[0]
            cx = na.take(cx,ind)
            cy = na.take(cy,ind)
            cz = na.take(cz,ind)
            dst = na.take(self.ds26,ind)
    
            tind = self.get_ind(cx,cy,cz)
    
            # only keep points in current label value of mask
            ind = self.getValidIndicies(tind)
        
            # now accumulate optional results
            inds = na.take(tind,ind)

            indc = [self.maskMap[i] for i in inds]
            results = {}
            if( coordinates ):
                cx = na.take(cx,ind)
                cy = na.take(cy,ind)
                cz = na.take(cz,ind)
                results['coordinates'] = (cx,cy,cz)
            if( distances ):
                results['distances'] = na.take(dst,ind)
            if( figuresOfMerit ):
                results['figuresOfMerit'] = na.take(self.fom, indc)
                
        
            #return cx,cy,cz,dst,ind
            return indc, results
        except Exception as error:
            print("failed in getValidNeighborsInformation() ", error)
    def getInds(self,crds):
        """given the x,y,z coordinates return the corresponding 1D index
        
        data can be passed in either as a sequence of x,y,z crds
        or x, y, z can be passed in separately"""
        try:
            ind = []
            for crd in crds:
                ind.append(crd[0]+crd[1]*self.dim[0]+crd[2]*self.dim[0]*self.dim[1])
            return ind
        except:
            return None

    def get_ind(self,*q):
        """given the x,y,z coordinates return the corresponding 1D index
        data can be passed in either as a sequence of x,y,z crds
        or x, y, z can be passed in separately"""
        try:
            if( len(q) == 1 ):
                x = q[0][:,0]
                y = q[0][:,1]
                z = q[0][:,2]
            else:
                x = q[0]
                y = q[1]
                z = q[2]
            try:
                cx = (x+0.5).astype(na.int32)
                cy = (y+0.5).astype(na.int32)
                cz = (z+0.5).astype(na.int32)
            except:
                cx = int(x+0.5)
                cy = int(y+0.5)
                cz = int(z+0.5)
            ind = cx + cy*self.dim[0]+cz*self.dim[0]*self.dim[1]
            return ind
        except Exception as error:
            print(error)
            return None
            
    def getNeighbors( self, inds ):
        """find the neighbors of each index within the array of indicies (inds) within the mask.
    Return as 1D indices into the 3D image"""
        try:
            p = na.array([inds % self.dim[0],
                          (inds/self.dim[0])%self.dim[1],
                          inds/(self.dim[0]*self.dim[1])]).astype(na.int16)

            #create an array in a specific shape containing ones
            ones = na.ones((len(inds),1),na.int16)
            #assigning a binary value of 1 to each index within the mask
            crds = na.concatenate((p,ones),axis=1)
            
            neighbors = na.dot(crds,self.d26)
            nInds =\
                [self.get_ind(neighbors[:,i],
                              neighbors[:,i+1],
                              neighbors[:,i+2]) for i in range(0,78,3)]
            # loop over the 26 columns to extract the neighbors in the mask
            nghbrs = {}
            for i in range(26):
                inds = self.mask.intersection(nInds[:,i])
                n = na.take(nInds[:,i],inds)
                nghbrs[i] = n
            return nghbrs
        except Exception as error:
            print("failed in getNeighbors() ", error)
            sys.exit()
        
    def createNXGraph( self, verbose = False ):
        """create a networkx graph that represents the relationship between each point in the currently labeled
    mask and each of its 26-point neighbors"""
        try:
            if(verbose):
                print("creating NXGraph")
            linds = len(self.inds)
            startTime = time.time()
            self.G = nx.Graph()

            for i in range(len(self.inds)):
                if( verbose and i % 10000 == 0):
                    print(i)
                neighbors, results = self.getValidNeighborsInformation(self.inds[i],distances=True,figuresOfMerit=True)
            
                # Add edges from the current point (ind) to each of its valid neighbors
                edgeCosts = self.cf(*(results['figuresOfMerit'],results['distances'],0))
                
                edges = [(i,neighbors[j],{'weight':edgeCosts[j]}) for j in range(len(neighbors))]
                #edges = [(i,neighbors[j],edgeCosts[j]) for j in range(len(neighbors))]
                self.G.add_edges_from(edges)
            self.createGraphTime = time.time()-startTime
            if( verbose ):
                print("graph creation time: ",self.createGraphTime)
        except Exception as error:
            print("failed in createNXGraph()", error)
    

    def getGraphTarget( self,  G):
        """look at the nodes of G (points within a labeled structure) and select 
    node within graph that has the maximum raw figure-of-merit value (by
    default, distance from edge)"""
        try:
            nodes = na.array(self.G.nodes())
            print("getGraphTarget",  nodes.max(), nodes.min())
            vals = na.take(self.rawFigureOfMerit,nodes)
            maxind = vals.argmax()
            return nodes[maxind]
        except Exception as error:
            print("failed in getGraphTarget()", error)
    def getDijkstraPaths(self, verbose=False):
        try:
            if( verbose ):
                print("+++Getting Dijkstra Paths+++")
            G = self.G
            seed = self.getGraphTarget()
            self.seed = seed
            self.paths = {}
            maxPath=-1
            maxPathNode = None
            count = 0
            self.paths = nx.single_source_dijkstra_path(G,seed)
            items = list(self.paths.items())
            items.sort( lambda x,y:int(len(x[1])-len(y[1])) )
            maxPathNode = items[-1][0] ; maxPathLength = len(items[-1][1])
            self.maxPathNode = maxPathNode    
            self.maxPath = maxPathLength
            print("maxPathNode =", maxPathNode)
            print("maxPathLength =", maxPathLength)
        except Exception as error:
            print("failed in getDijkstraPaths()", error)
            sys.exit()

    def getDijkstraPathsSingle(self, verbose=False):
        try:
            if( verbose ):
                print("getDijkstraPaths")
            G = self.G
            seed = self.getGraphTarget()
            self.seed = seed
            self.paths = {}
            maxPath=-1
            maxPathNode = None
            count = 0
            for node in G.nodes():
                if( verbose and count % 100==0 ):
                    print(count, node)
                count += 1
                
                self.paths[node] = nx.dijkstra_path(G,node,seed)
                if( maxPath < len(self.paths[node]) ):
                    maxPath = len(self.paths[node])
                    maxPathNode = node
                    
            print(maxPathNode,maxPath)
            self.maxPathNode = maxPathNode    
            self.maxPath = maxPath
        except Exception as error:
            print("failed in getDijkstraPaths()", error)
            sys.exit()

    def getEndPointPaths(self, verbose=False):
        """trace back shortest paths between detected endpoints and the graph
        target"""
    
        try:
            self.termInds = self.getInds(self.endpoints)
            if( verbose ):
                print("getEndPointPaths")
            G = self.G
            seed = self.getGraphTarget()
            self.seed = seed
            self.paths = {}
            maxPath=-1
            maxPathNode = None
            count = 0
            #tempP = nx.single_source_dijkstra_path(G,seed)
#            tempP = nx.floyd_warshall(G)
            for ind in self.termInds:
                node = self.maskMap[ind]
                try:
                    self.paths[node] = nx.astar_path(G,node,seed)
                    print("processed %d of %d endpoints"%(len(self.paths),len(self.termInds)))
                    if( maxPath < len(self.paths[node]) ):
                        maxPath = len(self.paths[node])
                        maxPathNode = node
                except Exception as error:
                    print("Could not create path from node",error)
            print(maxPathNode,maxPath)
            self.maxPathNode = maxPathNode    
            self.maxPath = maxPath
        except Exception as error:
            print("failed in getEndPointPaths()", error)
            sys.exit()
    def GenerateAstarPaths(self, inds,  G,  verbose=False): #Modified getEndpointPaths 
        """trace back shortest paths between detected endpoints and the graph
        target"""
        self.termInds = inds   
        maskMap = dict(list(zip(inds,list(range(len(inds))))))
        print("MaskMap",  maskMap)
        if(verbose):
            print("Identify A star paths")
            seed=self.getGraphTarget(G)
            print("seed", seed)
            paths={}
            maxPath=-1
            maxPathNode=None
            count=0
#            G = self.G
#            seed = self.getGraphTarget(G)
#            print "graph target success"
#            self.seed = seed
#            self.paths = {}
#            maxPath=-1
#            maxPathNode = None
            count = 0
            #tempP = nx.single_source_dijkstra_path(G,seed)
#            tempP = nx.floyd_warshall(G)
            for ind in self.termInds:
                node = self.maskMap[ind]
                try:
                    self.paths[node] = nx.astar_path(G,node,seed)
                    print("processed %d of %d endpoints"%(len(self.paths),len(self.termInds)))
                    if( maxPath < len(self.paths[node]) ):
                        maxPath = len(self.paths[node])
                        maxPathNode = node
                except Exception as error:
                    print("Could not create path from node",error)
            print(maxPathNode,maxPath)
            self.maxPathNode = maxPathNode    
            self.maxPath = maxPath
            
    def traceBackPaths4(self):
        """loop through the existing paths from longest to shortest and truncate
        paths when they intersect an existing path"""
        pathItems = list(self.paths.items())
        pathItems.sort(lambda x,y:len(x[1])-len(y[1]),reverse=True)
        rootPath = Path()
        rootPath.extend(pathItems.pop(0)[1])
        rootPath.intersection = self.seed
        self.splitPaths = [rootPath]
        starttime=time.time()
        count = 0
        while(pathItems):
            p = pathItems.pop(0)[1]
            count += 1
            for currentPath in self.splitPaths[::-1]:
                intersectPoint,cpI = findIntersectPoint2(currentPath,p)
                if( intersectPoint != -1 ):
                    uniquePath = Path()
                    uniquePath.extend(p[:intersectPoint])
                    uniquePath.intersection = intersectPoint
                    self.splitPaths.append(uniquePath)
                    #self.showPaths([currentPath,p[:intersectPoint],[self.seed]])
                    break

    def getSGPaths(self):
        """return the edge paths for the graph as a list of lists"""
        paths = []
        for n, nbrs in self.SG.adjacency_iter():
            for nbr, eattr in nbrs.items():
                paths.append([n]+eattr['path']+[nbr])
        return paths

    def traceBackPaths5(self):
        """splits paths traced between endpoints and target into individual
        segments connected by bifurcations.
        
        Currently I'm ending up with gaps at the bifurcations. This needs to be
        fixed."""
        pathItems = list(self.paths.items())
        pathItems.sort(lambda x,y:len(x[1])-len(y[1]),reverse=True)
        
        # create a networkx graph to hold the segments
        self.SG = nx.DiGraph()

        rootPath = pathItems.pop(0)[1]
        if( self.seed != rootPath[-1] ):
            print("incorrect root path")
            return
        self.SG.add_edge(rootPath[-1],rootPath[0],path=rootPath[-2:0:-1])
        starttime=time.time()
        count = 0
        while(pathItems):
            p = pathItems.pop(0)[1]
            self.insertPath(p)


    def pruneSplitPaths(self):
        i = 0
        while(i < len(self.splitPaths) ):
            if( len(self.splitPaths[i]) < self.__minPathLength):
                del self.splitPaths[i]
            else:
                i += 1
    def get_costfunction(self ):
        try:
            print("+++++ get_costfunction +++++")
            self.traceBackMaskDictionary()
            self.generateDijkstraCostImg()
            return
        except Exception as error:
            print("failed in get_costfunction() ", error)
            sys.exit()

    def process(self):
        """This is the `main' method that invokes the tree generation steps"""
        try:
            print("+++++ process() +++++")
            #self.get_costfunction()
            self.labelMaskStructures()
            self.get_costfunction()
            # write out data
            self.save_cost_function_dijkstra()
        except Exception as error:
            print("failed in process() ", error)

    def getValidIndicies(self, points):
        """...
        What we want here is the indicies into points for members of points that are within the mask
    
        """
        try:
            inds = [ i for i in range(points.size) if points.flat[i] in self.maskSet ]
            return inds
        except Exception as error:
            print("failed in getValidIndicies", error)
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
        except Exception as error:
            print("failed in getMaskMips", error)
    def define3x3_2DEndpointKernels(self):
        """Define the binary masks used with the hit or miss
        filter to detect vascular endpoints"""
        try:
            self.khm2d = []
            k = na.zeros((3,3),na.int8)
            k[1,1] = 1

            for i in range(3):
                for j in range(3):
                    if( i == 1  and j == 1 ):
                        pass
                    else:
                        kij = k.copy()
                        kij[i,j] = 1
                        self.khm2d.append(kij)
            print("%d kernels created"%len(self.khm2d))
        except Exception as error:
            print("failed in define3x3_2DEndpointKernels", error)

    def hitOrMiss2DDetection(self,mask,buffer):
        try:
            hm = na.zeros(mask.shape,na.int8)
            for k in self.khm2d:
                hm += ndi.binary_hit_or_miss(mask,k)
            crds = na.nonzero(hm)
            binds = buffer[crds[0],crds[1]]
            return crds,binds
        except Exception as error:
            print(error)
    def endPointsFromCritPoints(self,fname):
        """Convert critical points file into an endpoints list. I'll need to
        gneralize this sot ath I can specify my rules for specifying which
        coordiantes (if any) to ignore"""
        fo = open(fname,'rb')
        data = pickle.load(fo)
        self.endpoints = set([])
        for d in data:
            if( d.getLabel()=='mipz' ):
                self.endpoints.add( (d[0],d[1],self.zbuffer[d[1],d[0]]) )
            elif( d.getLabel()=='mipy' ):
                self.endpoints.add( (d[0],self.ybuffer[d[2],d[0]],d[2]) )
            elif( d.getLabel() == 'mipx' ):
                self.endpoints.add( (self.xbuffer[d[2],d[1]],d[1],d[2]) )
        
        print("%d unique endpoints identified"%len(self.endpoints))

    def endPointDetection2D(self):
        self.endpoints = set([])
        cxy,cz = self.hitOrMiss2DDetection(self.zmip,self.zbuffer)
        print("%d endpoints detected in zmip"%len(cz))
        for i in range(len(cz)):
            self.endpoints.add((cxy[1][i],cxy[0][i],cz[i]))
        cxz,cy = self.hitOrMiss2DDetection(self.ymip,self.ybuffer)
        print("%d endpoints detected in ymip"%len(cy))
        for i in range(len(cy)):
            self.endpoints.add((cxz[1][i],cy[i],cxz[0][i]))
        cyz,cx = self.hitOrMiss2DDetection(self.xmip,self.xbuffer)
        print("%d endpoints detected in xmip"%len(cx))
        for i in range(len(cx)):
            self.endpoints.add((cx[i],cyz[1][i],cyz[0][i]))

        print("%d unique endpoints identified"%len(self.endpoints))

    def viewEndPoints(self):
        """view the detected endpoints superimposed on the MIP images"""
        try:
            pyplot.gray()
            tmpz = self.zmip.copy()
            tmpy = self.ymip.copy()
            tmpx = self.xmip.copy()
            for c in self.endpoints:
                tmpz[c[1],c[0]] = 2
                tmpy[c[2],c[0]] = 2
                tmpx[c[2],c[1]] = 2
            pyplot.subplot(221)
            pyplot.imshow(tmpz)
            pyplot.subplot(222)
            pyplot.imshow(tmpy)
            pyplot.subplot(223)
            pyplot.imshow(tmpx)
            
            pyplot.show()
        except Exception as error:
            print("failed in veiwEndPoints", error)
    def insertPathAtNode(self,parentNode,childNode,insertPoint,path):
        """inserts a path into the object Segment Graph. Placement of insertion
        is specified by parentNode,childNode and insertPoint
        If childNode is not None then a new bifurcation is created. Otherwise
        the path is attached to an existing bifurcation"""
        if( not path ):
            return
        if( childNode == None ):
            # this path connects directly to an existing bifurcation
            # no need to split a path
            # I need to reverse the direction of the path because it was
            # originally defined from endpoint to seed whereas our directed
            # graph proceeds from seed to endpoints
            self.SG.add_edge(parentNode,path[0],path=path[-1:1:-1])
        else:
            # need to split the existing path between parentNode and childNode
            currentPath = self.SG[parentNode][childNode]['path']
            cp1 = currentPath[:insertPoint]
            cp2 = currentPath[insertPoint+1:]
            bifurcation = currentPath[insertPoint]

            self.SG.remove_edge(parentNode,childNode)
            self.SG.add_edge(parentNode,bifurcation,path=cp1)
            self.SG.add_edge(bifurcation,childNode,path=cp2)
            checkUniqueness(path[-1:1:-1],self.SG)

            self.SG.add_edge(bifurcation,path[0],path=path[-1:1:-1])

    def insertPath(self,path):
        """Insert the given path into the objects SegmentGraph"""

        for k in range(len(path)):
            p = path[k] 
                
            for n, nbrs in self.SG.adjacency_iter():
                # check to see if path equals n
                if(n == p ):
                    self.insertPathAtNode(n,None,None,path[:k])
                    return 
                for nbr, eattr in nbrs.items():
                    # check to see of path node equals nbr
                    if( nbr == p ):
                        self.insertPathAtNode(nbr,None,None,path[:k])
                        return
                    currentPath = eattr['path']
                    if( p in currentPath ):
                        bifurcation = currentPath.index(p)
                        self.insertPathAtNode(n,nbr,bifurcation,path[:k])
                        return 
                         
def findIntersectPoint2(a,b):
    for i in range(len(b)):
        bb = b[i]
        if( bb in a ):
            return i,a.index(bb)
    return -1,None

def findIntersectPoint(a,b):
    try:
        code = """
        #line 786 "treesearch.py" 
        int mb = b.length() ; 
        int ma = a.length() ;
        int found = false ;
        for( int i = 0; i < mb ; i++ ){
            //std::cout << "i="<<i << std::endl ;
            int bv = b[i] ;
            for( int j = 0 ; j < ma ; j++ ){
                int av = a[j] ;
                //std::cout << "a["<<i<<"]="<<av<<" b["<<j<<"]="<<bv<<std::endl;
                if( av == bv ){
                    //std::cout<< "matched"<<std::endl ;
                    //std::cout << "a["<<j<<"]="<<av<<" b["<<i<<"]="<<bv<<std::endl;
                    return_val = PyInt_FromLong(i);
                    found = true ;
                    break ;
                }


                    
            }
            if( found )
                break ;

        }
        if( found == false ){
            return_val = PyInt_FromLong(-1) ;
        }"""

        return weave.inline(code,['a','b'])
    except Exception as error:
        print(error)
       
def checkUniqueness(newPath,graph):
    setnp = set(newPath)
    for n, nbrs in graph.adjacency_iter():
        for nbr, eattr in nbrs.items():
            currentPath = eattr['path']
            notUnique = setnp.intersection(currentPath)
            if( notUnique ):
                print("newPath is not unique from path between (%d,%d)"%(n,nbr))
                print(notUnique)
                print('*'*42)

#def test_nxvascDijkstra():
#    """tests the information gathered using the Dijkstra algorithm"""
#    import pp
#    import imageTools.ITKUtils.io as io
#    import numpy as na
#    import fomFuncs
#    import costFuncs
#    import time
#    ppservers=()
#    job_server=pp.Server(ppservers=ppservers)
#    print "Test directional Dijkstra using parallel python"
#    """Uses sets for determining bifurcation points"""
#    img=io.readImage("tree2.mha", returnITK=False,  imgMode='uchar')
#    mask = na.where(img>0,1,0)
#    vx=nxvasc()
#    vx.setMask(mask)
#    vx.generateRawFigureOfMeritData()
#    vx.setFigureOfMeritF(fomFuncs.fomf1)
#    vx.setCostFunction(costFuncs.cf1)
#    vx.createMaskDictionary()
#    vx.fillFigureOfMerit()
#    start_time=time.time()
#    task1=job_server.submit(vx.createNXGraph, (verbose=True), )
#    result1=task1()
#    print "Task 1 Create NXGraph Complete:time taken =",  time.time()-start_time
#    task2=job_server.submit(vx.getDijkstraPaths(verbose=True)) #uses the dijkstra algorithm to find paths
#    result2=task2()
#    print "Task 2 Dijkstra Complete: time taken=",  time.time()-start_time
#    task3=job_server.submit(traceBackPaths4())
#    result3=task3()
#    print "Task 3 traced paths Complete: time taken=",  time.time()-start-time
#    task4=job_server.submit(pruneSplitPaths())
#    result4=task4()
#    print "Task 4 Pruned Paths:time taken=",  time.time()-start.time()
#    task5=job_server.submit(showPaths(paths.values()))
#    result5=task5()
#    print "Task 5 Show Paths:time taken=",  time.time()-start.time()
#    raw_input('continue')
#    task6=jobs_server.submit(showPaths(splitPaths,label="Orthogonal MIP Images with Centerlines"))
#    result6=task6()
#    print "Task 6 Show Centerlines: time taken=",  time.time()-start_time
#    raw_input('continue')
#    task7=job_server.submit(plotPaths(splitPaths,label="firstPlot",show=True))
#    result7=task7()
#    print "Task 7 Show plot: time taken=",  time.time()-start_time
#    print "FINISHED: Overall time to complete all tasks=",  time.time()-start_time
#    job_server.print_stats()
##    
#if __name__ == '__main__':
#    test_nxvascDijkstra()
