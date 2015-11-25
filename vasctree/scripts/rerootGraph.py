#!/usr/bin/env python
import networkx as nx
import sys
import numpy as np
import vasctrees.viewGraph as viewGraph
import vasctrees.SkeletonGraph as sg
import vasctrees.utils as utils
import argparse
def getGraph(d,i,label="og_rms"):
    try:
        key = (i,label)
        return d[key],key
    except:
        return getGraph(d,i+1,label=label)

def rerootGraph(graph,newRoot):
    og = graph.copy()
    oldRoot = og.graph['root']
    path = nx.shortest_path(og,oldRoot,newRoot)
    og.graph["root"] = newRoot
    reMap = []
    for i in range(len(path)-1):
        d = og[path[i]][path[i+1]]
        d['path'] = d['path'][::-1]
        d['wpath'] = d['wpath'][::-1]
        print("%d surface points"%len(d['mappedPoints']))
        og.remove_edge(path[i],path[i+1])
        og.add_edge(path[i+1],path[i],attr_dict=d)
        sg.fitEdge(og,(path[i+1],path[i]))
    
# I wonder if I need to reorder the edge attributes?
    sg.safelyRemoveDegree2Nodes(og, reMap)
    edges = og.out_edges(og.graph['root'], data=True)
    for e in edges:
        print(list(e[2].keys()))

    #viewGraph.viewGraph2(og,root=og.graph['root'])
    #raw_input('continue')
    print("%d points to remap"%len(reMap))
    sg.defineOrthogonalPlanes(og)
    sg.remapVoxelsToGraph(og, reMap)
    sg.mapPointsToPlanes(og)
    return og

def getParser():
    try:
        parser = argparse.ArgumentParser(description="rerootGraph.py command line parser")
        parser.add_argument("-f","--file",dest='fname',
                          help='name or directory for fixedImage')
        parser.add_argument("--meanx",action='store_true', dest='do_meanx',
                default=False)
        parser.add_argument("--medianx",action='store_true', dest='do_medianx',
                default=False) 
        parser.add_argument("--label",dest="graphLabel",default="mp_graphs")
        parser.add_argument("--number",dest="graphNumber",default=1,type=int)
        parser.add_argument("--rms",action='store_true', dest='do_rms',
                default=False)
        parser.add_argument("--set_label",dest='root_label', default=[],nargs=3)

        return parser
    except Exception as error:
        print("failed in getParser", error)  
        sys.exit(0)               

def main():
    parser = getParser()
    options = parser.parse_args()

    data = utils.readGraphs(options.fname)
    ogs = data['orderedGraphs']
    key = (options.graphNumber,options.graphLabel)
    if( key not in ogs ):
        key = utils.getOrderedGraphKeys(data['orderedGraphs'])

    if options.root_label:
        graph,key = getGraph(data['orderedGraphs'],1,label=options.graphLabel)

    print("procesing graph with key",key)
    num = key[0]
    label = key[1]

    graph = data['orderedGraphs'][key]

    if( options.do_medianx):

        endp = [n for n in graph.nodes() if graph.degree(n)==1]
        endpa = np.array(endp)
        medianx = np.median(endpa[:,0])
        print("computing based on graph median of",medianx)
        endp.sort(key=lambda n: abs(n[0]-medianx))
        newRoot = endp[0]
        ng_medianx = rerootGraph(graph,newRoot)
        ng_medianx.graph["root description"] = "root based on graph median x"
        viewGraph.viewGraph2(ng_medianx, root=ng_medianx.graph['root'], fileName=options.fname+".medianx",view=False)
        data['orderedGraphs'][(num,label+"_reroot_medianx")] = ng_medianx
    if( options.do_meanx ):
        meanx = np.mean(endpa[:,0])
        print("computing based on graph mean of",meanx)
        endp.sort(key=lambda n: abs(n[0]-meanx))
        newRoot = endp[0]
        ng_meanx = rerootGraph(graph,newRoot)
        ng_meanx.graph["root description"] = "root based on graph mean x"
        viewGraph.viewGraph2(ng_meanx, root=ng_meanx.graph['root'], fileName=options.fname+".meanx", view=False)
        data['orderedGraphs'][(num,label+"_reroot_meanx")] = ng_meanx

# Now what if I take the center most (say 50%) inner nodes and then pick
# the node with the minimum z value

    if( options.do_rms ):
        endp = [(n[0],n[1]['wcrd']) for n in graph.nodes(data=True) if graph.degree(n[0]) == 1]
        endpa = np.array([n[0] for n in endp])
        maxk = np.max(endpa[:,2])
        endp.sort(key=lambda n: np.sqrt((n[0][0]-256)**2+(n[0][1]-0)**2+(n[0][2]-maxk)**2))
        endp_sub = endp # endp[::len(endp)/2]
        print("examining %d of %d endpoints"%(len(endp_sub),len(endp)))
        #endp_sub.sort(key=lambda n: n[0][2])
        print(endp)
        print("selecting root node",endp_sub[0])
        newRoot = endp[0][0]
        ng_minz = rerootGraph(graph, newRoot)
        ng_minz.graph["root description"] = "root based on mn z for center x nodes"
        viewGraph.viewGraph2(ng_minz, root = ng_minz.graph['root'], fileName="%s_%d_%s.rms"%(options.fname,num,label), view=False)
        data['orderedGraphs'][(num,label+"_reroot_rms_ijk")] = ng_minz

    if( options.do_rms or options.do_meanx or options.do_medianx):
        utils.writeGraphs(data,options.fname)

if __name__ == '__main__':
    main()
