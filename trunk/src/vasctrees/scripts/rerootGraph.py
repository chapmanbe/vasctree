#!/usr/bin/env python
import networkx as nx
import gzip
import cPickle
import sys
import numpy as np
import vasctrees.viewGraph as viewGraph

def readGraphs():
    try:
        fo = gzip.open(sys.argv[1],"rb")
        data = cPickle.load(fo)
        fo.close()
    except:
        fo = file(sys.argv[1],"rb")
        data = cPickle.load(fo)
        fo.close()
    return data

def rerootGraph(graph,newRoot):
    og = graph.copy()
    oldRoot = og.graph['root']
    path = nx.shortest_path(og,oldRoot,newRoot)
    og.graph["root"] = newRoot
    for i in xrange(len(path)-1):
        d = og[path[i]][path[i+1]]
        og.remove_edge(path[i],path[i+1])
        og.add_edge(path[i+1],path[i],attr_dict=d)
# I wonder if I need to reorder the edge attributes?
    return og
def main():

    data = readGraphs()
    num = int(sys.argv[2])
    label = sys.argv[3]

    graph = data['orderedGraphs'][(num,label)]

    endp = [n for n in graph.nodes() if graph.degree(n)==1]
    endpa = np.array(endp)
    medianx = np.median(endpa[:,0])
    print "computing based on graph median of",medianx
    endp.sort(key=lambda n: abs(n[0]-medianx))
    newRoot = endp[0]
    ng_medianx = rerootGraph(graph,newRoot)
    ng_medianx.graph["root description"] = "root based on graph median x"
    viewGraph.viewGraph2(ng_medianx, root=ng_medianx.graph['root'])
    data['orderedGraphs'][(num,label+"_reroot_medianx")] = ng_medianx
    meanx = np.mean(endpa[:,0])
    print "computing based on graph mean of",meanx
    endp.sort(key=lambda n: abs(n[0]-meanx))
    newRoot = endp[0]
    ng_meanx = rerootGraph(graph,newRoot)
    ng_meanx.graph["root description"] = "root based on graph mean x"
    viewGraph.viewGraph2(ng_meanx, root=ng_meanx.graph['root'])
    data['orderedGraphs'][(num,label+"_reroot_meanx")] = ng_meanx

    fo = gzip.open(sys.argv[1],"wb")
    cPickle.dump(data,fo)
    fo.close()

if __name__ == '__main__':
    main()
