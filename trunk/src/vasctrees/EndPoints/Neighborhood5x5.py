import os
import sys
#import vasctrees.nxvasc as nxvasc
sys.path.append('../')
import nxvasc
import cPickle
import numpy as na
import scipy
import math
#import imageTools.ITKUtils.io as io
import dicom

class Neighborhood5x5(object):

    def __init__(self):
        self.maskMap = {}
        self.maskSet = None 
        self.dim = None
                  
    def get5x5matrix(self): #modified from nxvasc get3x3matrix()
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
        except Exception, error:
            print "failed in get5x5matrix(): ", error
    
    def setMask(self, mask):
        """Set the mask using the numpy image mask. In addition to reading the
        mask, the 1D indicies into the 3D image are generate and stored"""
        try:
            self.mask = mask
            self.inds = na.nonzero(self.mask.flat)[0]
            #print "length of self.inds",len(self.inds)
            #print self.inds
            self.dim = self.mask.shape[::-1]
            #print self.mask.shape
            return True
        except Exception, error:
            print "failed in setMask", error    
    
    def createMaskDictionary(self):
        """Create dictionary that maps the index into the 3D volume to an index into the mask
    The 1D array into the 3D volume is the key of the dictionary.
    The ordinal position of the index is the value """
        try:
            self.maskMap = dict(zip(self.inds,range(len(self.inds))))
            self.maskSet = set(self.inds)
        except Exception, error:
            print "failed in createMaskDictionary", error
            
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
    def get_crds(self,ind):
        """Given an array of 1D indicies into the image, return an Nx3 ??? array of the x,y,z coordinates"""
        try:
            ind = na.array(ind)
            nx = self.dim[0]
            ny = self.dim[1]
            nxny = self.dim[0]*self.dim[1]
            crd = na.transpose(na.array([ (ind % nx), (ind / nx)%ny,ind / nxny]))
            return crd
        except Exception, error:
            print "failed in get_crds ", error
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
                    na.inner(self.d124,\
                    na.array([p[0],p[1],p[2],1])),\
                             (124,3))
            cx = new_pnts[:,0]
            cy = new_pnts[:,1]
            cz = new_pnts[:,2]
            ind = na.nonzero((cx >=0 )*( cx < self.dim[0])*\
                             (cy >=0 )*( cy < self.dim[1])*\
                             (cz >=0 )*( cz < self.dim[2]))[0]
            cx = na.take(cx,ind)
            cy = na.take(cy,ind)
            cz = na.take(cz,ind)
            dst = na.take(self.ds124,ind)
    
            tind = self.get_ind(cx,cy,cz)
    
            # only keep points in current label value of mask
            ind = self.getValidIndicies(tind)
        
            # now accumulate optional results
            inds = na.take(tind,ind)

            indc = [self.maskMap[i] for i in inds]
            return indc
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
        except Exception, error:
            print error
            return None        
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
