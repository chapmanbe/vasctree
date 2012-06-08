"""
Contains a definition of Path, a class that is a subclass of RelatedPoints. Path
is conceived as an ordered set of RelatedPoints that define a connected path
through an N-dimensional domain.

Methods are added to reverse the order of the path, split the path into subpaths
and fit the path with a least squares spline
"""
import numpy
from RelatedPoints import *
from scipy.interpolate.fitpack import splev
from scipy.interpolate.fitpack import splprep

class Path(RelatedPoints):

    #def __new__(subtype, data, dim=3, size = None, dtype=None,copy=None):
        #    return RelatedPoints.__new__(subtype,data,dim=dim,size=size,dtype=dtype,copy=copy)
    def __array_finalize__(self,obj):
        super(Path,self).__array_finalize__(obj)
        self.children = []
    #def __init__(self, *args):
        #    self.dimensionality = 3
        #    self.dSz = None
        #    super(Path,self).__init__(*args)

        #self.children = []

    def __str__(self):
        txt =super(Path,self).__str__()
        txt += """\nchildren\n"""
        for c in self.children:
            txt += c.__str__()
        return txt
    def reverse(self):
        """Reverses in place the order of the points. this assumes a sense of
        ordering and is why it is added to the Path class rather than the
        RelatedPoints class"""
        temp = self.__getitem__(slice(None,None,-1)).copy()
        self.__setitem__(slice(None,None,None),temp)

    def getCost(self,cmap, costs):
        """For a mapping from the path coordinates to the costs domain
        return the cost associated with the path"""
        inds = []
        for i in self.__iter__():
            inds.append(cmap[i])
        return numpy.take(costs,inds)

    def split(self,cutPoints):
        """splits the path into a set of N subpaths defined by the N-1 cutpoints
        contained in cutPoints"""
        subPaths = []
        # I need to split the path in a redundant way so that the first element
        # of a child path corresponds to the last element of the parent path
        while(cutPoints):
            cutPoint = cutPoints.pop()
            subPaths.append(Path(self.__getitem__(slice(cutPoint,None,None)),
                           dim=self.dimensionality,
                           size = self.dSz))
            self = \
            Path(self.__getitem__(slice(None,cutPoint+1,None)),dim=self.dimensionality,size=self.dSz)
        return self,subPaths

    def fitPath(self,maxiter=40, s=20000):
        """fits a least squares spline through the path
        find descriptions of maxiter and s from scipy documentation"""
        try:
            pth = path.getCrds()
            pp = [pth[:,0],pth[:,1],pth[:,2]]
            if( len(pp[0]) <= 3 ): # there are not enough points to fit with
                self.splinePoints = pp
                self.splineTangents = None
                self.splineCurvature = None
                return 
            else:
                s = len(pp[0])/2.0
                cont = 1
                j=0
                while( j < maxiter ):
                    fit2 = splprep(pp,task=0,full_output =1, s=s)[0]
                    u = na.array(range(pp[0].shape[0]+1)).\
                            astype(na.float64)/(pp[0].shape[0])
                    # location of spline points
                    self.splinePoints = splev(u,fit2[0],der=0)
                    # first derivative (tangent) of spline
                    valsd = splev(u,fit2[0],der=1)
                    self.splineTangents = na.array(valsd).astype(na.float64)
                    # second derivative (curvature) of spline
                    valsc = splev(u,fit2[0],der=2)
                    self.splineCurvature = na.array(valsc).astype(na.float64)
                    success = 1 # this doesn't make much sense
                    if( success ): # how should I be determining success?
                        break
                    else:
                        s = s*0.9
                    j += 1
                return True
        except Exception, error:
            print "failed in fitPath()",error


