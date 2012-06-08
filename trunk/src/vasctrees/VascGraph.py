import networkx as nx
class VascGraph(object):
    def __init__(self, g):
        self.G = g
    
    def getAPaths(self, seed, points):
        self.paths = {}
        for node in points:
            self.paths[node] = nx.astar_path(self.G,node,seed)

    def setMinPathLength(self,mpl):#determines how short a path can be to be considered a path
        """set the minimum number of voxels that constitute a path"""
        self.__minPathLength = mpl
    def getMinPathLength(self):
        """return the minimum number of voxels that constitute a path"""
        
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
                        print "points do not match at ends but point is common to both paths"
            return children
        except Exception, error:
            print "failed in findSegmentChildren()",error
            
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

        print maskz.max()
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
            
    def fit_ordered_paths(self,maxiter=5):
        """loop through all the ordered paths and fit a least squares (smoothing spline) to the centerline"""
        try:
            for tkey in self.trees.keys():
                tree = self.trees[tkey]
                keys = tree.keys() 
                ftree = {}
                for key in keys:
                    seg = tree[key]
                    data = self.fit_path(self.paths[seg.segmentNumber],maxiter)
                    ftree[key] = data
                    self.ftrees[tkey] = ftree
            
        except Exception, error:
            print "failed in fit_ordered_paths()",error
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
            cPickle.dump([self.fpaths,self.paths,self.ftrees],fo,save_mode)
            fo.close()
        except Exception, error:
            print "failed in save_fit_paths()",error
            sys.exit()

    def save_path_data(self,suffix="_rpaths.pckle", save_mode=1):
        """save the path data into a cPickle file. save_mode=True saves the file in a binary format"""
        try:
            if( save_mode):
                omode = "wb"
            else:
                omode = "w"
            fo = open(self.outputFile+self.vsuffix+suffix,omode)
            cPickle.dump([self.paths,self.visited,self.trees,self.terminals],fo,save_mode)
            fo.close()
        except Exception, error:
            print "failed in save_path_data()",error
            sys.exit()

    def traceBackPaths4(self):
        """loop through the existing paths from longest to shortest and truncate
        paths when they intersect an existing path"""
        pathItems = self.paths.items()
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
