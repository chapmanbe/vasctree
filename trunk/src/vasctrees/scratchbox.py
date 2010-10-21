import networkx as nx
import numpy as np
import cPickle
import imageTools.imageUtils.basicImageUtils as biu
import matplotlib.pyplot as pplot
import imageTools.ITKUtils.io as io
import imageTools.ITKUtils.view as view
import imageTools.browse.a3d as a3d

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
def getNodeSubgraph(g, node, depth=4):
    """???"""
    nodes = set(getNodeSuccessors(g,[],[node],0,maxdepth=depth)+
                getNodePredecessors(g,[],[node],0,maxdepth=depth))
    h = g.subgraph(nodes)
    return h
def grabImageRegion(g, img,buffer=20):
    bb = getGraphBoundingBox(g)
    sz = img.shape
    # nodes and crds are stored in traditional (x,y,z) rather than numpy's (x,y,x)
    bs = ((max(bb[0][0]-buffer,0),min(bb[0][1]+buffer,sz[2]-1)),
          (max(bb[1][0]-buffer,0),min(bb[1][1]+buffer,sz[1]-1)),
          (max(bb[2][0]-buffer,0),min(bb[2][1]+buffer,sz[0]-1)))
          
    subimg = img[bs[2][0]:bs[2][1]+1,bs[1][0]:bs[1][1]+1,:]#bs[0][0]:bs[0][1]+1]
    return subimg, bs

def scaleImage(img, spacing):
    """returns an isotropic version of img, wih scaling based on voxel spacing
    provided in spcaing"""
    ms = float(min(spacing))
    #reverse the order to match numpy's reversed indexing
    img2 = ndi.zoom(img,[spacing[2]/ms,spacing[1]/ms,spacing[0]/ms])
    return img2
def scaleIndex(ind,scl):
    newInd = (int(ind[0]*scl[0]+0.5),int(ind[1]*scl[1]+0.5),int(ind[2]*scl[2]+0.5))
    return newInd
def scaleGraph(g, spacing):
    """returns a scaled copy of g with scaling determined by spacing
    g: a NetworkX graph
    spacing: the voxel spacing for the associated image"""
    if( g.is_directed() ):
        h = nx.DiGraph()
    else:
        h = nx.Graph()
    ms = float(min(spacing))    
    scl [spacing[0]/ms, spacing[1]/ms, spacing[2]/ms]
        
    edges = g.edges(data = True)
    for n1,n2,data in edges:
        n1b = scaleIndex(n1,scl)
        n2b = scaleIndex(n2,scl)
        path = data['path']
        newPath = []
        for p in path:
            p2 = scaleIndex(p,scl)
            newPath.append(p2)
        h.add_edge(n1b,n2b,path=newPath)
    return h
    
def insertGraphInImage(g, vimg):
    

    for node in g.nodes():
        vimg[node[2],node[1],node[0]] += 2000
    for edge in g.edges():
        path = g[edge[0]][edge[1]].get('path')
        if(path):
            for p in path:
                vimg[p[2],p[1],p[0]] += 1000
    return vimg
def getGraphBoundingBox(g):
    crds = np.array(g.nodes())
    bbox = ((crds[:,0].min(),crds[:,0].max()),(crds[:,1].min(),crds[:,1].max()),(crds[:,2].min(),crds[:,2].max()))
    return bbox
def visualizeXY_MPL(g,img,buffer=20):
    simg = insertGraphInImage(g,img)
    simg,bs = grabImageRegion(g,simg)
    print bs
    print g.nodes()
    locs = np.array(g.nodes())
    print locs
    #pos = dict(zip(g.nodes(),zip(locs[:,0],locs[:,1])))
    pos = dict(zip(g.nodes(),zip(locs[:,0],locs[:,1]-bs[1][0])))#-bs[0][0])))
    mipz = simg.max(axis=0)
    pplot.clf()
    pplot.imshow(biu.win_lev(mipz, 800, 1000))
    pplot.gray()
    nx.draw_networkx_nodes(g,pos,node_size=5, alpha=0.5)
    nx.draw_networkx_edges(g,pos,alpha=0.5)
    pplot.show()
    #pplot.savefig("viewxy.png")
    raw_input('continue')
    
def pickRandomNodeOfDegree(g,degree=4):
    import random
    d1 = [item[0] for item in g.degree().items() if item[1] == degree]
    node = random.choice(d1)
    return node
    
def main():
    fo = file("../Skeletons/PE00000_edited_skeleton_graphs.pckle","rb")
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
    print dg.max(), dg.min(), dg.mean()
    img = io.readImage("PE00000.mha",returnITK=False,imgMode='sshort')
    
    #img2 = img.copy()
    #vimg = insertGraphInImage(g,img2)
    #a3d.call(data = [vimg])
    #for i in range(20):
    #    randomNode = pickRandomNodeOfDegree(g)
    #    h = getNodeSubgraph(g,randomNode)
    #    
    #    visualizeXY_MPL(h,img,buffer=20)
    fo = file("../Skeletons/PE00000_edited_skeleton_graphs_pruned.pckle","wb")
    cPickle.dump(g,fo)
def main2():
    fo = file("../Skeletons/PE00000_edited_skeleton_graphs_pruned.pckle","rb")
    g = cPickle.load(fo)

    img = io.readImage("PE00000.mha",returnITK=False,imgMode='sshort')
    
    img2 = img.copy()
    vimg = insertGraphInImage(g,img2)
    for i in range(20):
        randomNode = pickRandomNodeOfDegree(g)
        h = getNodeSubgraph(g,randomNode)
        
        visualizeXY_MPL(h,img,buffer=20)
    
if __name__ == '__main__':
    main()
    main2()
