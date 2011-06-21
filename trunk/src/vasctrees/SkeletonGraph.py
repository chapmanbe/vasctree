#!/usr/bin/env python
# Need to select license to use
import networkx as nx
import numpy as np
import sys
import cPickle
import os
import imageTools.browse.a3d as a3d
#import itk
import subprocess
import cmvtg
import scipy.ndimage as ndi
import matplotlib.pyplot as plt
import math
import dicom
from scipy.interpolate.fitpack import splev
from scipy.interpolate.fitpack import splprep

class SkeletonGraph(object):
    """Class defined for identifying the neighbors (generating the graphs) of each point within a skeleton, 
    to model the shape of the vasculture
    img must be an ITK image"""
    def __init__(self, img):
        self.spacing = (1,1,1)
        self.graphs = {}
        self.orderedGraphs = {}
        self.roots = {}
        self.bifurcations = {}
        self.endpoints = {}
        self.currentGraphKey = 0
        self.Dim3Crds=[]
        self.Dim3={}
        self.img = img
        self.oimg = None
    def findNearestNode(self,val):
        """compute the distance from val to every node in the current graph. """
        nodes = self.cg.nodes()
        nlocs = np.array(nodes)
        rootInd = ((nlocs-val)**2).sum(axis=1).argmin()
        return nodes[rootInd]
    def __setCurrentGraphKey(self, key): #for counting through the graphs, tells you the graph currently being produced or looped through
        self.currentGraphKey = key
    def setOriginalImage(self,img=None):
        if( img!= None ):
            self.oimg = img
    def setCurrentGraph(self, key = None):
        """can choose to loop through a specific points neighbors by choosing that graph"""
        if( key != None ):
            self.__setCurrentGraphKey(key)
        self.cg = self.graphs[self.currentGraphKey]
    def getLargestOrderedGraphKey(self):
        """Return the key associated with the largest ordered graph"""
        keys = self.orderedGraphs.keys()
        szs = np.array([self.orderedGraphs[k].number_of_nodes() for k in keys ])
        ind = np.argmax(szs)
        return keys[ind]
    def setLargestGraphToCurrentGraph(self):
        keys = self.graphs.keys()
        szs = np.array([self.graphs[k].number_of_nodes() for k in keys ])
        ind = np.argmax(szs)
        self.setCurrentGraph(keys[ind])
    def getGraphsFromSkeleton(self, verbose = True):
        """Function for generating the graphs from the skeleton. For each point in the skeleton, 
        a graph is generated consisting of that points neighbors"""
        sz = self.img.shape
        if( verbose ):
            print "labeling skeleton image"
        lmask = ndi.label(self.img,structure=np.ones((3,3,3)))
        if( verbose ):
            print "found %d distinct object(s) in skeleton"%lmask[1]
        for i in range(1,lmask[1]+1):
            m = np.where(lmask[0]==i,1,0).astype(np.uint8)
            crds = np.array(np.nonzero(m)[::-1]).transpose().astype(np.int32)
            if( verbose ): print "generating graph from skeleton"
            g = cmvtg.getGraphsFromSkeleton(m,crds)
            if( verbose ):
                self.cg = g
                self.viewCurrentGraph()
            ep, bif = cmvtg.findEndpointsBifurcations(g)
            #print "Number of pre-pruning bifurcations",len(bif)
            g = cmvtg.pruneUndirectedBifurcations(g,bif)
            if( verbose ):
                self.cg = g
                self.viewCurrentGraph()
            ep, bif = cmvtg.findEndpointsBifurcations(g)
            #print "Number of post-pruning bifurcations",len(bif)
            self.graphs[i] = g

    def viewGraph(self,graph = None):
        """view a graph. If no graph is specified, the current graph is drawn."""
        plt.clf()
        if( graph == None ):
            graph = self.cg
        nodes = graph.nodes()
        d = graph.degree()
        pos_xy = {}
        pos_xz = {}
        pos_yz = {}
        sz = []
        for n in nodes:
            pos_xy[n] = n[:2]; pos_xz[n] = n[::2]; pos_yz[n] = n[1:]
            sz.append(3*d[n])
        fig = plt.figure(0)
        fig.add_subplot(221)
        plt.title("x-y view")
        nx.draw(graph,pos_xy,with_labels=False, node_size = sz)
            
        fig.add_subplot(222)
        plt.title("x-z view")
        nx.draw(graph,pos_xz,with_labels=False, node_size = sz)
                
        fig.add_subplot(223)
        plt.title("y-z view")
        nx.draw(graph,pos_yz,with_labels=False, node_size = sz)
        fig.show()
        fig.savefig("currentGraph.png")
        raw_input('continue')
    ###THE FOLLOWING FUNCTIONS ARE USED TO HELP WITH ORDERING THE GRAPHS
    
    def createPathToBifurcation(self, e): #NOT YET USED IN EVALUATEVASCMODEL.PY
        """Need to identify paths between bifurcation points,
        all points identified in findEndpointsBifurcations"""
        path = []
        cn = e
        while( True ):
            path.append(cn)
            ns = nx.neighbors(self.cg,cn)
            for n in ns:
                if( n not in path ):
                    if( n in self.bifurcations ):
                        return n, len(path), path
                    else:
                        cn = n
        return
                
        
    def findEndpointsBifurcations(self, verbose = False):
        """For the current graph, identify all points that are either
        endpoints (1 neighbor) or """+\
        """bifurcation points (3 neighbors)"""
        endpoints = []
        bifurcations = []
        for n in self.cg.nodes_iter():
            if( nx.degree(self.cg,n) == 1 ):
                endpoints.append(n)
            elif( nx.degree(self.cg,n) >= 3 ):
                bifurcations.append(n)
        self.endpoints[self.currentGraphKey] = endpoints
        self.bifurcations[self.currentGraphKey] = bifurcations
    def selectSeedFromDFE(self):
        """For the current graph, set the root to be the node nearest the
        maximum DFE location. Uses a chamfer distance measure to save time"""
        try:
            dfe = self.dfe
        except:
            oimg = self.oimg
            self.dfe = ndi.distance_transform_cdt(oimg)
            dfe = self.dfe
        if( self.bifurcations[self.currentGraphKey] ):
            nds = np.array(self.bifurcations[self.currentGraphKey])
        else:    
            nds = np.array(self.cg.nodes())
        if( nds.shape[0] == 1 ): # there is only one node to choose from so use it for seed
            return (nds[0,0],nds[0,1],nds[0,2])
        vals = dfe[nds[:,2],nds[:,1],nds[:,0]]
        mi = vals.argmax()
        return (nds[mi,0],nds[mi,1],nds[mi,2])
    def traceEndpoints(self, key=0):
        """Uses the bidirectional dijkstra to traceback the paths from the endpoints"""
        og = nx.DiGraph()
        currentRoot = self.roots[(self.currentGraphKey,key)]
        endpoints = self.endpoints[self.currentGraphKey]
        bifurcations = self.bifurcations[self.currentGraphKey]
        cg = self.graphs[self.currentGraphKey]
        print "current root is",currentRoot
        for e in endpoints:
            plen, path = nx.bidirectional_dijkstra(cg, currentRoot, e)
            i = 0
            start = currentRoot
            path = path[1:]
            while( path ):               
                try:
                    if( path[i] in bifurcations ):
                        og.add_edge(start,path[i],path=path[:i])
                        start = path[i]
                        path = path[i+1:]
                        i = 0
                    else:
                        i += 1
                except IndexError:
                    og.add_edge(start,e,{'path':path[:-1]})
                    path = None
        self.orderedGraphs[(self.currentGraphKey,key)] = og

    def setRoots(self, origins):
        """Define where to stop tracing back, defined point on the pulmonary trunk"""
        o = np.array(origins)
        sz = self.img.shape
        nxy = sz[2]*sz[1]
        for g in self.graphs.keys():
            endpoints = self.endpoints[g]
            crds = np.array([((i%sz[2]),(i/sz[2])%sz[1],i/(nxy)) for i in endpoints])
            avgX = np.average(crds[:,0])
            dx = np.abs(o[:,0]-avgX)
            mind = np.argmin(dx)
            origin = o[mind,:]
            d = crds - origin
            d = d*d
            d = d.sum(axis=1)
            self.roots[g] = endpoints[d.argmin()]
    def setRoot(self, origin, key=0):
        """Define the point on the graph closest to origin as the root of the graphs.
        For now I'm going to be very simple-minded and just look for the nearest
        node. In actuality, we'd expect the origin to not be a bifurcation"""
        try:
            matchedNode = self.findNearestNode(origin)
            self.roots[(self.currentGraphKey,key)] = matchedNode
        except Exception, error:
            print "failed in setRoot", error
    
    ###OTHER FUNCTIONS
    def deleteDegree2Nodes(self, key):
        """Delete all degree 2 nodes (except for the root node if it is degree 2)"""
        og = self.orderedGraphs[key]
        dgs = og.degree()
        root = self.roots[key]
        
        for n,d in dgs.items():
            if( d == 2 and n != root):
                print "deleting node",n
                pred = og.predecessors(n)[0]
                succ = og.successors(n)[0]
                p1 = og[pred][n]['path']
                p2 = og[n][succ]['path']
                newEdge = p1+[n]+p2
                og.remove_node(n)
                og.add_edge(pred,succ,path=newEdge)
                    
     
                             
    def prunePaths(self, key, threshold=5):
        """Removes terminal paths that are considered to be too short
        to be part of the skeleton
        
        Can I rewrite this in a more functional way?"""
        og = self.orderedGraphs[key]
        dgs = og.degree()
        for n,d in dgs.items():
            if( d == 1 ):
                p = og.predecessors(n)[0]
                path = og[p][n]['path']
                if( len(path) < threshold ):
                    og.remove_node(n)
                    
            
    def saveGraphs(self,name):
        fo = open(name,'wb')

        cPickle.dump({'imgShape':self.img.shape,'skelGraphs':self.graphs,
                      'orderedGraphs':self.orderedGraphs,'roots':self.roots},fo)
        
        
    def insertGraphInImage(self, vimg):
        for key in self.orderedGraphs.keys():
            g = self.orderedGraphs[key]
            for node in g.nodes():
                vimg.flat[node] += 2000
            for edge in g.edges():
                path = g[edge[0]][edge[1]].get('path')
                if(path):
                    vimg.flat[path] += 1000

    def fitEdges(self, key):
        """fits a least squares spline through the paths defined for the
        orderedGraph indexed by key
        
        If a fit is possible, the following key-value pairs are added to an edge
        
        'd0': the resampled points
        'd1': The first derivative computed at each re-sampled point
        'd2': The second derivative computed at each re-sampled point.
        
        """
        og = self.orderedGraphs[key]
        edges = og.edges()
        for e in edges:
            path = og[e[0]][e[1]]['path']
            path.extend([e[1]])
            p = [e[0]]
            p.extend(path)
            ae = np.array(p)
            
            if( ae.shape[0] > 3 ): # there are not enough points to fit with

                s = ae.shape[0]/2.0

                fit2 = splprep(ae.transpose(),task=0,full_output =1, s=s)[0]
                u = np.array(range(ae.shape[0]+1)).\
                        astype(np.float64)/(ae.shape[0])
                # location of spline points
                og[e[0]][e[1]]['d0'] = splev(u,fit2[0],der=0)
                # first derivative (tangent) of spline
                og[e[0]][e[1]]['d1'] =np.array( splev(u,fit2[0],der=1))
                # second derivative (curvature) of spline
                og[e[0]][e[1]]['d2'] = np.array(splev(u,fit2[0],der=2))

    
    def makeOrthogonalPlane(self, key):
        for e in edges:
            path = og[e[0]][e[1]]['path']
            path.extend([e[1]])
            p = [e[0]]
            p.extend(path)
            ae = np.array(p)

        og = self.orderedGraphs[key]
        edges = og.edges(data=True)
        for e in edges:
           d0 = e['d0']
           d1 = e['d1']
           numPoints = len(d0[0])
           p = np.zeros((numPoints))

        for i in range(numPoints):
                   d0i = np.array((d0[0][i],d0[1][i],d0[2][i]))
                   d1i = np.array((d1[0][i],d1[1][i],d1[2][i]))
                   p[i] = -np.inner(d0i,d1i)
 
                   checkData()
          
    def checkData():
        """ get data from the data basic,
            get the diameter.
            while loop to check all the point in the diameter range
            if the dot product is the same dot product. make the plant
        """    
        img = dicom.read_file("57_pulm_vasc_seg_clean_median_True_closing_True_kernel_1_1_1_1.dcm")
        pdata = img.pixel_array
                
        inRange = pdata.max(axis =0)
        #find the closest point to d0
        #  the 
        if (j < d0 and j > d0[2]):
              
         while(inRange):
           try:
               for j in range(inRange):
                 d0j = np.array((d0[0][j],d0[1][j],d0[2][j]))
                 d1j = np.array((d1[0][j],d1[1][j],d1[2][j]))
                 newp[j] = -np.inner(d0j,d1j)
                 
                 if( newp[j] == p[i] ):
                     
                  #  xs = x[i:i+5] # slice each layer
                    ys = y[i:i+5]
                  #  zs = z[i:i+5]
                  #  layer = ys[0] # since in this case they are all equal.

                   # fig = plt.figure(0)

                    #ax.draw(graph,xs,ys,zs)
                   # fig.show() 
                 else:
                        j += 1
           except Exception:
                print "index out of bound  "
                
    
          
def pruneUndirectedBifurcations(cg,bifurcations, verbose= True):    
    # get the total number of connected components in the current graph
    
    for b in bifurcations:
        cg = deleteExtraEdges(cg,b)
    return cg
        

def deleteExtraEdges(cg, b):            
    ndist = {}
    print type(cg)
    numConnected = nx.number_connected_components(cg)
    print "number of nodes is ",cg.number_of_nodes()
    for n in cg.neighbors(b):   
        # test whether deleting the edge between n and b increases
        # the number of connected components
        cg.remove_edge(b,n)
        newNumConnected = nx.number_connected_components(cg)
        if( newNumConnected == numConnected ): # then this could be a valid deletion
            # compute the step distance from n to its neighbor b
            print "the edge between %s and %s can be cut without changing the topology of the graph"%(b,n)
            ndist[(b,n)] = math.sqrt((n[0]-b[0])**2+(n[1]-b[1])**2+(n[2]-b[2])**2)
        cg.add_edge(b,n)
    if( ndist ):
        items = ndist.items()
        #rearrange node,distance pairing so we can sort on distance
        k,v = zip(*items)
        items = zip(v,k)
        maxNeighbor = max(items)
        # cut the maximum step length edge that is valid to cut
        print "removing edge",maxNeighbor[1][0],maxNeighbor[1][1]
        cg.remove_edge(maxNeighbor[1][0],maxNeighbor[1][1])
        cg = deleteExtraEdges(cg,b)
    return cg
