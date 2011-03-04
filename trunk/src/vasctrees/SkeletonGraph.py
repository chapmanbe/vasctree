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
import cmvtg
import scipy.ndimage as ndi
import matplotlib.pyplot as plt


class SkeletonGraph(object):
    """Class defined for identifying the neighbors (generating the graphs) of each point within a skeleton, 
    to model the shape of the vasculture
    img must be an ITK image"""
    def __init__(self, img):
        self.img = itk.PyBuffer.IUC3.GetArrayFromImage(img)
        self.spacing = img.GetSpacing()
        self.graphs = {}
        self.orderedGraphs = {}
        self.roots = {}
        self.bifurcations = {}
        self.endpoints = {}
        self.currentGraphKey = 0
        self.Dim3Crds=[]
        self.Dim3={}
        self.oimg = None
    def findNearestNode(self,val):
        """compute the distance from val to every node in the current graph. """
        nodes = self.cg.nodes()
        nlocs = np.array(nodes)
        rootInd = ((nlocs-val)**2).sum(axis=1).argmin()
        return nodes[rootInd]
    def __setCurrentGraphKey(self, key): #for counting through the graphs, tells you the graph currently being produced or looped through
        self.currentGraphKey = key
    def setOriginalImage(self,img=None, fname= None):
        if( img ):
            self.oimg = img
        elif( fname ):
            self.oimg = io.readImage(fname,imgMode='uchar',returnITK=False)
    def setCurrentGraph(self, key = None):
        """can choose to loop through a specific points neighbors by choosing that graph"""
        if( key != None ):
            self.__setCurrentGraphKey(key)
        self.cg = self.graphs[self.currentGraphKey]
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
            print "Number of pre-pruning bifurcations",len(bif)
            g = cmvtg.pruneUndirectedBifurcations(g,bif)
            if( verbose ):
                self.cg = g
                self.viewCurrentGraph()
            ep, bif = cmvtg.findEndpointsBifurcations(g)
            print "Number of post-pruning bifurcations",len(bif)
            self.graphs[1] = g

    def viewCurrentGraph(self):
        nodes = self.cg.nodes()
        d = self.cg.degree()
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
        nx.draw(self.cg,pos_xy,with_labels=False, node_size = sz)
            
        fig.add_subplot(222)
        plt.title("x-z view")
        nx.draw(self.cg,pos_xz,with_labels=False, node_size = sz)
                
        fig.add_subplot(223)
        plt.title("y-z view")
        nx.draw(self.cg,pos_yz,with_labels=False, node_size = sz)
        fig.show()
        fig.savefig("currentGraph.png")
        raw_input('continue')
    ###THE FOLLOWING FUNCTIONS ARE USED TO HELP WITH ORDERING THE GRAPHS
    
    def createPathToBifurcation(self, e): #NOT YET USED IN EVALUATEVASCMODEL.PY
        """Need to identify paths between bifurcation points, all points identified in findEndpointsBifurcations"""
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
        """For the current graph, identify all points that are either endpoints (1 neighbor) or """+\
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
        maximum DFE location"""
        try:
            dfe = self.dfe
        except:
            oimg = self.oimg
            self.dfe = ndi.distance_transform_cdt(oimg)
            dfe = self.dfe
        if( self.bifurcations ):
            nds = np.array(self.bifurcations[self.currentGraphKey])
        else:    
            nds = np.array(self.cg.nodes())
        if( nds.shape[0] == 1 ): # there is only one node to choose from so use it for seed
            return (nds[0,0],nds[0,1],nds[0,2])
        vals = dfe[nds[:,2],nds[:,1],nds[:,0]]
        mi = vals.max()
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
    def deleteTreeEdge(self, nd, threshold = 5):
        """delete or merge the edge from nd to its predecessor"""
        try:
            predecessor = self.cg.predecessors(nd)
            if( len(predecessor) > 1 ):
                print "incorrect number of predecessors" # raise exception
                return
            p = predecessor[0]
            edge = self.cg.get_edge_data(p, nd)
            if( self.cg.degree(p) == 2 ):
                # merge the edges
                p2  = self.cg.predecessors(p)
                e2 = self.cg.get_edge_data(p2,p)
                newEdge = e2['path']+[p]+edge['path']
                self.cg.remove_edges_from([(p2,p),(p,n)])
                self.cg.add_edge(p2,n,path=newEdge)
            else:
                self.cg.remove_node(nd)
        except Exception, error:
            print "failed in deleteTreeEdge", error
     
                             
    def prunePaths(self, threshold=5):
        """Removes paths that are considered to be too short to be part of the skeleton"""
        for e in self.map.keys():
            if(self.map[e][1] < threshold):
                self.cg.remove_nodes_from( self.map[e][2] )
                self.map.pop(e)
            
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
