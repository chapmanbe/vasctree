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


class SkeletonGraph(object):
    """Class defined for identifying the neighbors (generating the graphs) of each point within a skeleton, 
    to model the shape of the vasculture"""
    def __init__(self, img):
        self.img = img
        self.graphs = {}
        self.orderedGraphs = {}
        self.roots = {}
        self.bifurcations = {}
        self.endpoints = {}
        self.currentGraphKey = 0
        self.Dim3Crds=[]
        self.Dim3={}
    def findNearestNode(self,val):
        """compute the distance from val to every node in the current graph. Assumes both
        nodes and val are 1D indicies into the image"""
        nodes = self.cg.nodes()
        nlocs = np.array([np.unravel_index(n, self.img.shape) for n in nodes])
        vloc = np.unravel_index(val, self.img.shape)
        dist = ((nlocs-vloc)**2).sum(axis=1)
        rootInd = np.argmin(dist)
        return nodes[rootInd]
    def __setCurrentGraphKey(self, key): #for counting through the graphs, tells you the graph currently being produced or looped through
        self.currentGraphKey = key
        
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
    def getGraphsFromSkeleton(self):
        """Function for generating the graphs from the skeleton. For each point in the skeleton, 
        a graph is generated consisting of that points neighbors"""
        sz = self.img.shape
        nxy = sz[1]*sz[2]
        
        # create an array of indices pointing to the nonzero locations in the image
        inds = np.nonzero(self.img.flat)[0]
        mask = np.ones(sz,np.int32)*-1
        
        # create a new image populated with the skeleton locations
        mask.put(inds,inds)
        inds = list(inds)
        #numpy array goes z,y,x
        graphNum = 0 #should equal the number of points in the skeleton once completed
        while( inds ):
            # while there are are still points not added to a graph
            # create a new graph
            G = nx.Graph()
            que = [inds.pop()]
            while( que ):
                ind = que.pop()
                # convert from 1D to 3D coordinate
                crd = (np.unravel_index(ind,sz))
                # get the neighbors of ind in 3 dimensions constrained by image boundary
                s = (max(0,crd[0]-1),max(0,crd[1]-1),max(0,crd[2]-1))
                e = (min(sz[0],crd[0]+2),min(sz[1],crd[1]+2),min(sz[2],crd[2]+2))
                subimg = mask[s[0]:e[0],s[1]:e[1],s[2]:e[2]]
                neighbors = subimg.take(np.where(subimg.flat > -1)[0])

                for nn in neighbors:
                    if (ind != nn ):
                        G.add_edge(ind,nn)
                        # remove nn from our master list and add it to the que
                        try:
                            inds.remove(nn)
                            que.append(nn)
                        except ValueError:
                            pass
                if( G.number_of_nodes() % 1000 == 0 ):
                    print G.number_of_nodes(), len(inds)
            print "Number of unassigned points: %d"%len(inds)#should count down
            self.graphs[graphNum] = G #STORES THE GRAPH for each point
            print "Num of nodes in current graph", G.number_of_nodes()
            graphNum += 1

            
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
        
    def traceEndpoints(self, key=0):
        """Uses the bidirectional dijkstra to traceback the paths from the endpoints"""
        try:
            og = nx.DiGraph()
            currentRoot = self.roots[(self.currentGraphKey,key)]
            endpoints = self.endpoints[self.currentGraphKey]
            bifurcations = self.bifurcations[self.currentGraphKey]
            cg = self.graphs[self.currentGraphKey]
            print "current root is",currentRoot
            for e in endpoints:
                plen, path = nx.bidirectional_dijkstra(cg, currentRoot, e)
                i = 0
                start = self.roots[(self.currentGraphKey,key)]
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
        except Exception, error:
            print "failed in traceEndpoints", error
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
        except Excpetion, error:
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
