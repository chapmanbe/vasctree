"""
This module defines a class that provides a container for related points. The
class inherits from the numpy.ndarray class. I don't really know what I am doing
with this: I followed examples from
http://mentat.za.net/numpy/numpy_advanced_slides/http://mentat.za.net/numpy/numpy_advanced_slides/
The class in the array component of the class, the points are stored. The points
are stored as 1-D arrays into an N-dimensional space. The dimensionality of the
space (e.g. 3D) is specified in the dimensionality attribute and the size of the
domain from which the points are taken is specified in the dSz attribute.

The class contains a derived attribute, crds, that is computed from the 1D
array. However, in order to preserve data consistency, I want to make this is
private variable so that the user can only modify the 1D array.
"""

import numpy
class RelatedPoints(numpy.ndarray):

    def __new__(subtype, data, dim=3, size = None, dtype=None,copy=None):
        p = numpy.array(data,dtype=dtype,copy=copy)
        p = p.view(subtype)
        p.dimensionality = dim
        p.dSz = size
        return p
    def __array_finalize__(self,obj):
        self.dimensionality = getattr(obj,'dimensionality',{})
        self.dSz = getattr(obj,'dSz',{})

    def __str__(self):
        txt = """dimensionality: %d; dSz: %s\n"""%(self.dimensionality,self.dSz)
        txt +="""RelatedPoints: %s\n"""%super(RelatedPoints,self).__str__()
        return txt
    def setDomainSize(self,sz):
        if( len(sz) != self.dimensionality ):
            print "incorrect dimension"
            return
        else:
            self.dSz = tuple(sz[:])
    def setDimensionality(self,dim):
        self.dimensionality = dim
    def getMinimumDistance2(self,p):
        """computes the minimum distance between the group of points and the given point
        p. Can this be sped up by doing it with arrays?
        """
        try:
            d = (self.crds[:,0]-p[0])**2 + \
                (self.crds[:,1]-p[1])**2 + \
                (self.crds[:,2]-p[2])**2
            return d.min()
        except Exception, error:
            print 'failed in getMinimumDistance2', error
            print self.crds.shape, p.shape
    def getCrds(self):
        """Return the crds attribute (N-dimensional coordinate. If crds has not
        yet been computed, first compute. I want to change crds to be private"""
        try:
            return self.crds
        except:
            self.computeCrds()
            return self.crds
    def computeCrds(self):
        try:
            self.crds = numpy.transpose(numpy.array([
                self.__getitem__(slice(None,None,None)) % self.dSz[0],
                (self.__getitem__(slice(None,None,None)) / self.dSz[0])%self.dSz[1],\
                 self.__getitem__(slice(None,None,None))/(self.dSz[0]*self.dSz[1])]))
        except Exception, error:
            print "failed in get_crds ", error
            return -1
