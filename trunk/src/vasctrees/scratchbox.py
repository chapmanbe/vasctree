import networkx as nx
import numpy as np
import cPickle
import imageTools.imageUtils.basicImageUtils as biu


def prune(g):
    d1 = [item[0] for item in g.degree().items() if item[1] == 1]
    for d in d1:
        if( g.predecessors(d) ):
            
            p = g.predecessors(d)[0]
            edge = g.get_edge_data(p,d)['path']
            if( g.degree(p) == 2 ):
                try:
                    
                    p2 = g.predecessors(p)[0]
                    e2 = g.get_edge_data(p2,p)['path']
                    #print "removing",p
                    g.remove_node(p)
                    
                    #print "connecting",p2,d
                    g.add_edge(p2,d,path=e2+[p]+edge)
                    if( not checkTopConsistency(g) ):
                        raw_input('inconsistent graph after deleting edge %d %d %d'%(p2,p,d))
                except Exception, error:
                    print "failed to merge", error
            elif( len(edge) < 5 ):
                #print "removing",d, g.degree(d)
                g.remove_node(d)
                if( not checkTopConsistency(g) ):
                        raw_input('inconsistent graph after deleting edge %d %d'%(p,d))
        else:
            print "no predecessor for",d
            
def checkTopConsistency(g):
    tops = [n for n in g.nodes() if not g.predecessors(n)]
    if( len( tops ) == 1 ):
        return True
    else:
        print tops
        return False
def getNodePredecessors(g, nds, que, cd, maxdepth=2):
    if( cd >= maxdepth ):
        nds.extend(que)
        return nds
    else:
        newque = []
        while( que ):
            nd = que.pop(0)
            nds.append(nd)
            newque.extend(g.predecessors(nd))
        return getNodePredecessors(g, nds, newque,cd+1,maxdepth=maxdepth)
        
def getNodeSuccessors(g, nds, que, cd, maxdepth=2):
    if( cd >= maxdepth ):
        nds.extend(que)
        return nds
    else:
        newque = []
        while( que ):
            nd = que.pop(0)
            nds.append(nd)
            newque.extend(g.successors(nd))
        return getNodeSuccessors(g, nds, newque,cd+1,maxdepth=maxdepth)        
def getNodeSubgraph(g, node, depth=2):
    """???"""
    nodes = set(getNodeSuccessors(g,[],[node],0,maxdepth=depth))
    h = g.subgraph(nodes)
    return h
def getGraphBoundingBox(g,imgShape):
    crds = biu.get_crds(g.nodes(),data['imgShape'])
    bbox = ((crds[0].min(),crds[0].max()),(crds[1].min(),crds[1].max()),(crds[2].min(),crds[2].max()))
    return bbox
    
def main():
    fo = file("../Skeletons/PE00000_edited_skeleton_graphs_orig.pckle","rb")
    data = cPickle.load(fo)
    ogs = data["orderedGraphs"]
    g = ogs[(0,u'0')]
    oldSize = g.size()
    iter = 0
    while(True):
        prune(g)
        iter += 1
        newSize =  g.size()
        if( newSize == oldSize ):
            break
        else:
            oldSize = newSize
        print iter, oldSize
        
    dg = np.array(g.degree().values())
    print dg.max(), deg.min(), deg.mean()
    
if __name__ == '__main__':
    main()
