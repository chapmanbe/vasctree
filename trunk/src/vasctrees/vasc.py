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

import imageTools.ITKUtils.io as io
import os
import numpy as na
import scipy.ndimage as ndi
import math
import cPickle
import sys

import string
import VascSegment
from RelatedPoints import *
from Path import *
import matplotlib.pyplot as plt 
import imageTools.imageUtils.basicImageUtils as biu
import pylab
import time

#from scipy.interpolate.fitpack import *

class vasctree(object):
    """Basic class for processing and anayzing a vascular structure"""
    # define initialization routine
    def __init__(self,\
            fileroot=None,\
            cf = None):
        """Constructor for vasctree class.
       
        fileroot: filename for tree???

        cf: a Python function to be used as a cost function ??? provide a
        description
        """

        # initialize filenames
        self.vsuffix = "_vt"
        self.fileroot=fileroot
        self.outmode = 'postscript eps color "Times-Roman" 21' # to cut
        self.__fomFile = None
        self.maskfile = None

        # set up lists and dictionaries

        self.mask = None
        self.paths = []
        self.fpaths = []
        self.ftrees = {}
        self.tree = {}
        self.bifurcations = {}
        self.G = {}
        self.Neighbors = {}
        self.maskMap = {}
        self.current_label = 0
        # variabel functions
        self.epn = self.getNeighbors # determines neighbors of a point
        # book keeping variables
        self.bifurcation_num = 0
        self.term = 8
        self.__minPathLength = 0
        # cost function parameters
        self.recompute = 0
        self.cf = cf
        #self.fomf = self.fomf3
        self.fomf = None
        self.scale = [4,4,4]
        self.dim = None

        self.vmap = None

        self.get3x3matrix()

    # do we want to/need to define our own __del__ function? Had it in old versions

    def get3x3matrix(self):
        """define the 3x3 neighborhood relationship matrix, 
        find each point within the path and the 26 points closest to it"""
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
        except Exception, error:
            print "failed in get3x3matrix(): ", error
    def setCostFunction(self,func):
        self.cf = func
    def setFigureOfMeritF(self,func):
        self.fomf = func
    def setMinPathLength(self,mpl):
        self.__minPathLength = mpl
    def getMinPathLength(self):
        return self.__minPathLength
    def setOutputFile(self, outputFile):
        """Sets object output file to image located in outputFile"""
        self.outputFile = outputFile
    def getOutputFile(self):
        return self.outputFile
       
    def createValues(self):
        try:
            self.vals = na.ones(len(self.inds),na.float32)
            self.newsources = na.zeros(len(self.inds),na.int32)
        except Exception, error:
            print "failed in createValues", error
    def createMaskDictionary(self):
        """Create dictionary that maps the index into the 3D volume to an index
        into the mask
    The 1D array into the 3D volume is the key of the dictionary.
    The ordinal position of the index is the value
    """
        try:
            self.maskMap = dict(zip(self.inds,range(len(self.inds))))
            self.maskSet = set(self.inds)
        except Exception, error:
            print "failed in createMaskDictionary", error
    def setFigureOfMeritFile(self, fomFile):
        """Sets object figure of merit image to data in fomFile"""
        self.fomFile = fomFile
    def getFigureOfMeritFile(self):
        return self.fomFile
    def getRawFigureOfMerit(self):
        return self.rawFigureOfMerit
    def fillFigureOfMerit(self):
        """Generate fom data from the objects figure-of-merit function (fomf)"""
        try:
            self.fom = apply(self.fomf,(self.rawFigureOfMerit,))
        except Exception, error:
            print "failed in fillFigureOfMerit", error
    def generateRawFigureOfMeritData(self):
        """This function takes the msk file associated with self and computes
        a distance from edge map using scipy.ndimage.distance_transform_cdt

        The resulting distance map is assigned to a rawFigureOfMerit attribute of
        self"""

        try:
            dfe = ndi.distance_transform_cdt(self.mask)
            self.rawFigureOfMerit = dfe.take(self.inds)
        except Exception, error:
            print "failed in generateRawFigureOfMeritData", error
    def setMask(self,mask):
        """Set the mask using the numpy image pointed to by mask.
        In addition to the mask, the 1D indicies into the 3D image are 
        generated and stored"""
        try:
            self.mask = mask
            self.inds = na.nonzero(self.mask.flat)[0]
            print "length of self.inds",len(self.inds)
            self.dim = self.mask.shape[::-1]
            print self.mask.shape
            return True
        except Exception, error:
            print "failed in setMask", error
    def getMask(self):
        return self.mask

    def reverse_paths(self):
        """reverse the order of points in the path"""
        try:
            for p in self.paths:
                p.reverse()
        except Exception, error:
            print "failed in reverse_paths()", error

    def read_voxel_map(self, suffix = "_vm.pckle", read_mode = 1 ):
        try:
            if( read_mode ):
                omode = "rb"
            else:
                omode = "r"
            fo = open(self.maskfile+self.vsuffix+suffix,omode)
            data = cPickle.load(fo)
            self.map_inds = data[0]
            self.vmap = data[1]
            fo.close()
        except Exception, error:
            print "failed in read_voxel_map()", error


    def save_voxel_map(self, suffix="_vm.pckle", save_mode = 1):
        try:
            if( save_mode):
                omode = "wb"
            else:
                omode = "w"
                fo = open(self.maskfile+self.vsuffix+suffix,omode)
                cPickle.dump([self.map_inds,self.vmap],fo,save_mode)
                fo.close()
        except Exception, error:
            print "failed in save_voxel_map()",error
            sys.exit()

    def plotPaths(self, label='', show=False):
        """A quick and dirty plotting of the centerlines using pylab"""
        plt.clf()
        colors = ['r','g','b','y','p']
        nc = len(colors)
        for i in range(len(self.splitPaths)):
            p = self.splitPaths[i]
            try:
                imgInds = na.take(self.inds,list(p[1]))
                crds = self.get_crds(imgInds)
                plt.plot(crds[:,0],crds[:,1],"%s+"%colors[i%nc])
                                  
            except:
                pass

        plt.title(label)
        plt.xlim(0,32)
        plt.ylim(0,32)
        plt.savefig(label.replace(' ','')+".png")
        if( show ):
            plt.show()

        

    def save_path_data(self,suffix="_rpaths.pckle", save_mode=1):
        try:
            if( save_mode):
                omode = "wb"
            else:
                omode = "w"
            fo = open(self.maskfile+self.vsuffix+suffix,omode)
            cPickle.dump([self.paths,self.visited,self.trees,self.terminals],fo,save_mode)
            fo.close()
        except Exception, error:
            print "failed in save_path_data()",error
            sys.exit()
    def get_crds(self,ind):
        """Given an array of 1D indicies into the image, return an Nx3 array of the x,y,z coordinates"""
        try:
            ind = na.array(ind)
            nx = self.dim[0]
            ny = self.dim[1]
            nxny = self.dim[0]*self.dim[1]
            crd = na.transpose(na.array([ (ind % nx), \
                                          (ind / nx)%ny,\
                                           ind / nxny]))
            return crd
        except Exception, error:
            print "failed in get_crds ", error
            return -1


    def getValidNeighborsInformation(self, index,distances = False,
                                     coordinates=False,
                                     figuresOfMerit=False ):
        """ get the coordinates of all points within the 26-point neighborhood
        of index that lie within the mask.
    
    The function returns the indicies into the the 3D image by default 
    and the following values are returned optionally, depending on how 
    the flag values are set distances: The step distances between p 
    and each of its valid neighbors coordinates: The (x,y,z) coordinates 
    for each valid neighbor figureOfMerit: The point figure-of-merit for 
    each valid neighbor """
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
        except Exception, error:
            print "failed in getValidNeighborsInformation() ", error

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
        except:
            return None
            
    def getNeighbors( self, inds ):
        """find the neighbors of each index within the array of indicies 
        (inds) within the mask.  Return as 1D indices into the 3D image"""
        try:
            p = na.array([inds % self.dim[0],
                          (inds/self.dim[0])%self.dim[1],
                          inds/(self.dim[0]*self.dim[1])]).astype(na.int16)
            ones = na.ones((len(inds),1),na.int16)
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
        except Exception, error:
            print "failed in getNeighbors() ", error
            sys.exit()
        

    def createGraph( self, verbose=False ):
        try:
            if( verbose ):
                print "createGraph()"
            startTime = time.time()
            self.G = {}

            self.Neighbors = {}
            for i in xrange(len(self.inds)):
                if( verbose and i % 10000 == 0):
                    print i, " of ",len(self.inds)
                neighbors, results = \
                        self.getValidNeighborsInformation(self.inds[i],
                                                       distances = True,
                                                       figuresOfMerit = True )
                h ={}
                edgeCosts = apply(self.cf,(results['figuresOfMerit'],results['distances'],0))
                for j in range(len(neighbors)):
                    h[neighbors[j]] = edgeCosts[j]
                self.G[i] = h
            self.createGraphTime = time.time()-startTime
            if( verbose ):
                print "graph creation time: ",self.createGraphTime
        except Exception, error:
            print "failed in createGraph()", error
    
    def getBestSeedLabeled( self ):
        """look at labeled points and select remaining point with maximum CM value"""
        try:
            rinds = na.nonzero(self.__labels > -1)[0]
            vals = na.take(self.rawFigureOfMerit,rinds)
            maxind = vals.argmax()
            return rinds[maxind]
        except Exception, error:
            print "failed in getBestSeedLabeled()", error
    def getGraphTarget( self ):
        """look at the nodes of G (points within a labeled structure) and select 
    node within graph that has the maximum raw figure-of-merit value (by
    default, distance from edge)"""
        try:
            nodes = na.array(self.G.keys())
            print nodes.max(), nodes.min()
            vals = na.take(self.rawFigureOfMerit,nodes)
            maxind = vals.argmax()
            return nodes[maxind]
        except Exception, error:
            print "failed in getGraphTarget()", error
       
    def getDijkstraPaths(self, verbose = True ):
        """Identifies all potential paths through the centerline of the vascular tree. It stores them in 
        a dictionary paths. the key = index, value = the points along the path"""
        try:
            if( verbose ):
                print "+++++ getDijkstraPaths +++++"
    
            # Run Dijkstra's algorithm
            import Dijkstra
            G = self.G
            self.seed = self.getGraphTarget()
            self.paths = {}
            maxPath = -1
            maxPathNode = None
            count = 0
            dpaths = Dijkstra.Dijkstra(G,self.seed)
            items = dpaths[0].items()
            items.sort( lambda x,y:int(x[1]-y[1]) , reverse=True)

            self.paths = {}
            for ii in items:
                sind = ii[0]
                if( not self.paths.has_key(sind)):
                    path = [sind]
                    while(True):
                        try:
                            sind = dpaths[1][sind]
                            path.append(sind)
                        except:
                            break
                    self.paths[ii[0]]=path
            pathItems = self.paths.items() #creates a list of the paths
            pathItems.sort(lambda x,y: int(len(x[1])-len(y[1])),reverse=True) #sorts the paths by length, longest to shortest
            self.maxPathNode = pathItems[0][0] #Identifies the location of the longest path node, where it begins 
            self.maxPath = len(pathItems[0][1]) #Identifies the longest path

        except Exception, error:
            print "failed in getDijkstraPaths()", error
            sys.exit()
    def traceBackPaths(self):
        """Takes the maxPath and compares all other paths to it
        We are looking for areas along the paths that overlap to eliminate duplicate points"""
        pathItems = self.paths.items()#THINK THIS IS REDUNDANT??? Done in the FXN that preceeds this 
        pathItems.sort(lambda x,y:len(x[1])-len(y[1]),reverse=True)#THINK THIS IS REDUNDANT???
        self.splitPaths = [([],set(pathItems.pop(0)[1]))]
        while(pathItems):
            p = set(pathItems.pop(0)[1])
            intersections = []
            for i in range(len(self.splitPaths)):
                currentPath = self.splitPaths[i]
                if( currentPath[1].intersection(p) ):
                    p = p.difference(currentPath[1])
                    
                    intersections.append(i)
                    if(not p ):
                        break
            if( p ):
                self.splitPaths.append((intersections,p))
    def prunePaths(self):
        """Removes all paths that are shorter than the default minPathLength"""
        i = 0
        while(i < len(self.splitPaths) ):
            if( len(self.splitPaths[i][1]) < self.__minPathLength):
                del self.splitPaths[i]
            else:
                i += 1

    def generateDijkstraCostImg(self):
        """generate a 3D image of the cost function"""
        try:
            print "filling values"
            temp = na.zeros([self.dim[2],self.dim[1],self.dim[0]],na.Int16)
            na.put(temp.flat,self.inds,((1000.0/self.vals.max())*self.vals).astype(na.Int16))
            return temp
        except Exception, error:
            print "failed in generateDijkstraCostImg() ",error
            sys.exit()

    def get_costfunction(self ):
        """Calculates the cost, the closer the point is to th edge of the mask the higher the cost, 
        the farther the point, or closer to the centerline the lower the cost, based on the seed points"""
        try:
            print "+++++ get_costfunction +++++"
            # get list of newsources
            ind = na.nonzero(self.newsources > 0)
            iter = 0
            track_sources = []
            if( len(self.Neighbors) == 0 ):
                if( self.recompute or self.read_mask_dictionary(get_dictionaries=[1,0]) == 0 ):
                    self.defineMaskDictionary(define_dictionaries=[1,0])
                    self.save_mask_dictionary(save_dictionaries=[1,0])
            self.traceBackMaskDictionary()
            self.generateDijkstraCostImg()
            return
        except Exception, error:
            print "failed in get_costfunction() ", error
            sys.exit()

    def set_seeds(self,seeds = [[101,6,75]]):
        """specify the seed (target) points for generating the cost function"""
        try:
            self.seeds = seeds[:]
            for seed in seeds:
                print "setting seed ",seed
                imgind = self.get_ind(seed[0],seed[1],seed[2])
                listind = self.maskMap[imgind]
                self.vals[listind] = 0
                self.newsources[listind] = 1
        except Exception, error:
            print "failed in set_seeds() ",error
    def process(self):
        try:
            print "+++++ process() +++++"
            #self.get_costfunction()
            self.labelMaskStructures()
            # write out data
            self.save_cost_function_dijkstra()
        except Exception, error:
            print "failed in process() ", error
    def getArrayIndicies(self, inds):
        """To save memory I am representing the self.mask as a dictionary
           I thus need to replace the Numeric.take() functionality to get
           a list of indicies into the 1D arrays
           
           Make sure all indicies being looked at are within the mask and create array of them"""
        try:
            inds_1d = -1*na.ones(len(inds),na.int32)
            for i in range(len(inds)):
                if( self.maskMap.has_key(inds[i]) ):
                    inds_1d[i] = self.maskMap[inds[i]]
            return inds_1d
        except Exception, error:
            print "failed in get_array_indicies ", error
            return -1
    
    
#    def getArrayIndicies_labeled(self, path):
#        """To save memory I am representing the self.mask as a dictionary
#           I thus need to replace the na.take() functionality to get
#           a list of indicies into the 1D arrays"""
#        
#        #WHERE IS THIS FXN USED, NOT CALLED IN THE TEST OR WITHIN VASC.PY, IS IT NEEDED???
#        try:
#            inds = set(path).intersection(self.maskMap.keys())
#            inds_1d = []
#            for ind in inds:
#                if( self.__labels[self.maskMap[ind]] == self.current_label ):
#                    inds_1d.append(self.maskMap[ind])
#            return na.array(inds_1d)
#        except Exception, error:
#            print "failed in getArrayIndicies_labeled ", error
#            return -1
#
    def getValidIndicies(self, points):
        """Identifies the indicies that are within the current mask only"""
        try:
            inds = [ i for i in range(points.size) if points.flat[i] in self.maskSet ]
            return inds
        except Exception, error:
            print "failed in getValidIndicies", error
            return -1


    def splitPaths(self):
        """splits paths into individual segments"""
        try:
            self.generateVisitedList()
            origPathLength = len(self.paths)
            self.cutPoints = []
            for k in range(origPathLength):
                path = self.paths[k]
                inds = self.getArrayIndicies(path)
                # grab the number of times visited
                vinds = na.take(self.visited,inds)
                mvinds = na.nonzero(vinds > 1 )[0]
                cutPoints = list(mvinds)
                if( len(mvinds) ):
                    cutPoints = list(mvinds)
                    self.cutPoints.extend(path.take(cutPoints))
                    #print "splitting path into ",len(mvinds)+1," paths"
                    # there are multiple bifurcations existing along
                    # the path. Split inclusively
                    path, subpaths=path.split(cutPoints)
                    self.paths[k] = path
                    if( subpaths ):
                        self.paths.extend(subpaths)
                # now I delete to decrement the count number at points where we
                # cut the path
                cutAt = inds.take(mvinds)
                self.visited[cutAt] -= 1
        except Exception, error:
            print "failed in split_paths()",error
            sys.exit()
    def generateVisitedList(self):
        """could this be more efficient with sets?"""
        """Creates list of indicies for each location within an individual path?"""
        try:
            self.visited = na.zeros(len(self.vals),na.int32)
            for k in range(len(self.paths)):
                path = self.paths[k]
                inds = self.getArrayIndicies(path)
                na.put(self.visited,inds,na.take(self.visited,inds)+1)
        except Exception, error:
            print "Failed in generateVisitedList()", error


