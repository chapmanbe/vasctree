import numpy as np
cimport numpy as np
import cPickle
import numpy as np
import networkx as nx
import math

def measureDistToEdge(p,e):
    """p a 3D point stored in a numpy array
    e an edge stored in ???
    """
    cdef float mdist = 0
    cdef int esz = len(e)
    cdef int i
    #print e
    cdef float cdist = (p[0]-e[0][0])**2+(p[1]-e[0][1])**2+(p[2]-e[0][2])**2
    mdist = cdist
    for i in xrange(1,esz):
        cdist = (p[0]-e[i][0])**2+(p[1]-e[i][1])**2+(p[2]-e[i][2])**2
        mdist = min(cdist,mdist)
    return mdist
def mapPToEdge(p, g, verbose = True):
    """takes a graph g and """
    ge = g.edges(data=True)
    cdef int i
    cdef int j
    cdef int k
    cdef int minEdge 
    cdef int lsize = len(ge)
    cdef float cdist = 0.0
    cdef float mdist = 0.0
    if( len(ge[0][2]['path'])>1):
        print len(ge[0][2]['path'])
        mdist = measureDistToEdge(p,ge[0][2]['path'])
    minEdge = 0
    for j in xrange(1,lsize):
        if( len(ge[j][2]['path'])>1 ):
            #print len(ge[j][2]['path'])
            cdist = measureDistToEdge(p,ge[j][2]['path'])
            if( cdist < mdist ):
                mdist = cdist
                minEdge = j
    
    return minEdge

def getGraphsFromSkeleton(np.ndarray[np.uint8_t, ndim=3] mask,
                          np.ndarray[np.int32_t, ndim=2] crds):
    """Function for generating the graphs from the skeleton. For each point in the skeleton, 
    a graph is generated consisting of that points neighbors"""
   
    cdef int ncrds = crds.shape[0]
    cdef int szz = mask.shape[0]-1
    cdef int szy = mask.shape[1]-1
    cdef int szx = mask.shape[2]-1
    
    cdef Py_ssize_t l, i, j, k
    G = nx.Graph()
    for l in xrange(ncrds):
        crd = (crds[l,0],crds[l,1],crds[l,2])
        s = (max(0,crd[0]-1),max(0,crd[1]-1),max(0,crd[2]-1))
        e = (min(szx,crd[0]+2),min(szy,crd[1]+2),min(szz,crd[2]+2))

        for i in range(s[0],e[0]):
            for j in range(s[1],e[1]):
                for k in range(s[2],e[2]):
                    if (mask[k,j,i] and
                        ( i != crd[0] or j != crd[1] or k != crd[2] ) ):
                            G.add_edge(crd,(i,j,k))
                        
    return G

def findEndpointsBifurcations(cg):
    """For the current graph, identify all points that are either endpoints or bifurcations"""
    endpoints = []
    bifurcations = []
    for n in cg.nodes_iter():
        if( nx.degree(cg,n) == 1 ):
            endpoints.append(n)
        elif( nx.degree(cg,n) >= 3 ):
            bifurcations.append(n)
    return endpoints, bifurcations


def traceEndpoints(cg, endpoints, bifurcations, currentRoot):
    """Uses the bidirectional dijkstra to traceback the paths from the endpoints"""
    og = nx.DiGraph()
    cdef int i = 0
    for e in endpoints:
        plen, path = nx.bidirectional_dijkstra(cg, currentRoot, e)
        start = currentRoot
        path = path[1:]
        
        while( path ):               
            if( path[i] in bifurcations ):
                og.add_edge(start,path[i],path=path[:i])
                start = path[i]
                path = path[i+1:]
                i = 0
            else:
                i += 1

    return og
def pruneUndirectedBifurcations(cg,bifurcations, verbose= True):
    cdef Py_ssize_t i
    
    # get the total number of connected components in the current graph
    numConnected = nx.number_connected_components(cg)
    for b in bifurcations:
        ndist = {}
        
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
            cg.remove_edge(maxNeighbor[1][0],maxNeighbor[1][1])
        #print "minimum bifurcation dist",v.min()
        #if( v.min() < 1 ):
        #    print items
        #    raw_input('continue')
        # find the items that are not equal to the minimum step distance
        #ma = np.nonzero(v != v.min())[0]
        #if( len(ma) <= len(items) - 2):
        #    for i in range(len(ma)):
        #        if( cg.has_edge(k[ma[i]][0],k[ma[i]][1]) ):
        #            cg.remove_edge(k[ma[i]][0],k[ma[i]][1])
                    
            
    return cg
            
