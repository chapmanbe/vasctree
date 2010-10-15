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
from optparse import OptionParser


class SkeletonGraph(object):
    def __init__(self, img):
        self.img = img
        self.graphs = {}
        self.orderedGraphs = {}
        self.roots = {}
        self.bifurcations = {}
        self.endpoints = {}
        self.currentGraphNumber = 0
        
    def setCurrentNumber(self, num):
        self.currentGraphNumber = num
    def setCurrentGraph(self):
        self.cg = self.graphs[self.currentGraphNumber]

    def getGraphFromSkeleton(self):
        sz = self.img.shape
        indsk1 = np.nonzero(self.img.flat)[0]
        mask = np.zeros(self.img.shape,np.uint32)
        mask.put(indsk1,indsk1)
        
        
        nxy = sz[2]*sz[1]
        stackCrds = [(i/(sz[2]*sz[1]),(i/sz[2])%sz[1],(i%sz[2])) for i in indsk1]
        d1 = dict(zip(indsk1,stackCrds))
        graphNum = 0
        while( d1 ):
            G = nx.Graph()
            s = d1.keys()[0]
            que = {s:d1.pop(s)}
            while( que ):
                ind,crd = que.popitem()
                # get the neighbors of ind
                starts = (max(0,crd[0]-1),max(0,crd[1]-1),max(0,crd[2]-1))
                ends = (min(sz[0],crd[0]+2),min(sz[1],crd[1]+2),min(sz[2],crd[2]+2))
                n = mask[starts[0]:ends[0], starts[1]:ends[1], starts[2]:ends[2]]
                ninds = np.nonzero(n.flat)[0]
                neighbors = n.take(ninds)
                for nn in neighbors:
                    if (ind != nn ):
                        G.add_edge(ind,nn)
                        try:
                            que[nn] = d1.pop(nn)
                        except KeyError:
                            pass
            print len(d1)
            self.graphs[graphNum] = G 
            graphNum += 1

    def createPathToBifurcation(self, e):
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
                  

    def labelRoot(self, crds, origin):
        """find the endpoint that lies closests to the coordinate specified in origin
        use this as the root of the graph"""
        crds = np.array([endpoints%sx])
        stackCrds = [(i/(sz[2]*sz[1]),(i/sz[2])%sz[1],(i%sz[2])) for i in indsk1]
    def findEndpointsBifurcations(self, verbose = False):
        endpoints = []
        bifurcations = []
        for n in self.cg.nodes_iter():
            if( nx.degree(self.cg,n) == 1 ):
                endpoints.append(n)
            elif( nx.degree(self.cg,n) >= 3 ):
                bifurcations.append(n)
        self.endpoints[self.currentGraphNumber] = endpoints
        self.bifurcations[self.currentGraphNumber] = bifurcations
    def traceEndpoints(self):
        og = nx.DiGraph()
        currentRoot = self.roots[self.currentGraphNumber]
        endpoints = self.endpoints[self.currentGraphNumber]
        bifurcations = self.bifurcations[self.currentGraphNumber]
        cg = self.graphs[self.currentGraphNumber]
        print "current root is",currentRoot
        for e in endpoints:
            plen, path = nx.path.bidirectional_dijkstra(cg, currentRoot, e)
            i = 0
            start = self.roots[self.currentGraphNumber]
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
        self.orderedGraphs[self.currentGraphNumber] = og
                    
    def setRoots(self, origins):
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
        
        
    def prunePaths(self, threshold=5):
        for e in self.map.keys():
            if(self.map[e][1] < threshold):
                self.cg.remove_nodes_from( self.map[e][2] )
                self.map.pop(e)
            
    def saveGraphs(self,name):
        fo = open(name,'wb')

        cPickle.dump([self.graphs,self.orderedGraphs,self.roots],fo)
        
        
    def insertGraphInImage(self, vimg):
        for key in self.orderedGraphs.keys():
            g = self.orderedGraphs[key]
            for node in g.nodes():
                vimg.flat[node] += 2000
            for edge in g.edges():
                path = g[edge[0]][edge[1]].get('path')
                if(path):
                    vimg.flat[path] += 1000

def getParser():
    try:
        parser = OptionParser()
        parser.add_option("-i", "--img", dest="filename", help="binary image to read and threshold", default=".dcm")
        parser.add_option("-o", "--origins", dest="originsFile", help="file containing the arterial and venous origins for this subject",
                          default="")
        parser.add_option("-n", "--numIter", dest="iterations",type="int",default=10)

        return parser
    except Exception,  error:
        print "failed to generate parser",  error
        


def main():
    try:
        parser = getParser()
        (options, args) = parser.parse_args()
    
        #origins = cPickle.load(open(args.origFile,'rb'))
        #reader = itk.ImageFileReader.IUC3.New(FileName=options.filename)
        #filler = itk.VotingBinaryIterativeHoleFillingImageFilter.IUC3IUC3.New()
        #filler.SetMaximumNumberOfIterations(options.iterations)
        #filler.SetInput(reader.GetOutput())
        subprocess.call("gunzip %s"%options.filename+".gz",shell=True)
        tmp2 = os.path.splitext(options.filename)
        outFill = tmp2[0]+"_fill_%d.mha"%options.iterations
        outSkel = tmp2[0]+"_fill_%d_skel.mha"%options.iterations
        #writer = itk.ImageFileWriter.IUC3.New()
        #writer.SetInput(filler.GetOutput())
        #writer.SetFileName(outFill)
        #print "filling in holes in segmentation"
        #writer.Update()
        subprocess.call("iterVote %s %s 1 %d"%\
                        (options.filename,outFill,options.iterations),shell=True)
        subprocess.call("BinaryThinning3D %s %s"%(outFill,outSkel),shell=True)
        os.remove(outFill)
        img = io.readImage(outSkel,returnITK=False,imgMode = "uchar")
        sg = SkeletonGraph(img)
        print "generating graph from skeleton"
        sg.getGraphFromSkeleton()
        for i in range(len(sg.graphs)):
            print "processing graph %d"%i
            sg.setCurrentNumber(i)
            sg.setCurrentGraph()
            sg.findEndpointsBifurcations()
        #fo = open(pfile,'rb')
        #origins = cPickle.load(fo)
        #sg.setRoots(origins)
        #print "ordering graphs"
        #for i in range(len(sg.graphs)):  
        #    sg.setCurrentNumber(i)
        #    sg.traceEndpoints()       
        print "save the graphs"
        sg.saveGraphs(tmp2[0]+"_graphs.pckle")
        print "compress the image"
        subprocess.call("gzip %s %s"%(options.filename,outSkel),shell=True)
    except Exception, error:
        print "failed in getSeanModels due to error:",error
        print options.filename, outSkel

if __name__ == '__main__':
    main()
