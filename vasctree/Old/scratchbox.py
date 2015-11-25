import networkx as nx
import numpy as np
import cPickle
import imageTools.imageUtils.basicImageUtils as biu
import matplotlib.pyplot as pplot
import imageTools.ITKUtils.io as io
import imageTools.ITKUtils.view as view
import imageTools.browse.a3d as a3d
import itk
import scipy.ndimage as ndi
from mayaviCTA import viewImgWithNodes as viewImg
def prune(g):
    d0 = [item[0] for item in g.degree().items() if item[1] == 0]
    g.remove_nodes_from(d0)
    print "number of 0 degree nodes is",len(d0)
    d1 = [item[0] for item in g.degree().items() if item[1] == 1]
    for d in d1:
        if( g.predecessors(d) ):
            
            p = g.predecessors(d)[0]
            edge = g[p][d]['path']
            if( g.degree(p) == 2 ):
                try:
                    
                    p2 = g.predecessors(p)[0]
                    e2 = g[p2][p]['path']
                    #print "removing",p
                    g.remove_node(p)
                    
                    #print "connecting",p2,d
                    g.add_edge(p2,d,path=e2+[p]+edge)
                    if( not checkTopConsistency(g) ):
                        raw_input('inconsistent graph after deleting edge %s %s %s'%(p2,p,d))
                except Exception, error:
                    print "failed to merge", error
            elif( len(edge) < 5 ):
                #print "removing",d, g.degree(d)
                g.remove_node(d)
                if( not checkTopConsistency(g) ):
                        raw_input('inconsistent graph after deleting edge %s %s %s'%(p,d,edge))
        else:
            print "no predecessor for",d
    d0 = [item[0] for item in g.degree().items() if item[1] == 0]
    print "number of 0 degree nodes is now",len(d0)
    
def pruneTwosers(g, thresh=5):
    print g.size()
    d2 = [item[0] for item in g.degree().items() if item[1] == 2]
    for n in d2:
        p = g.out_edges([n],data=True)
        s = g.in_edges([n], data = True)
        if( p and s ):
            g.remove_node(n)
            newPath = p[0][2]['path']+[n]+s[0][2]['path']
            g.add_edge(p[0][0],s[0][1],path=newPath)
    print g.size()
def checkTopConsistency(g):
    tops = [n for n in g.nodes() if not g.predecessors(n)]
    if( len( tops ) == 1 ):
        return True
    else:
        #print tops
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
def getNodeSubgraph(g, node, depth=8):
    """???"""
    print 'depth is',depth
    nodes = set(getNodeSuccessors(g,[],[node],0,maxdepth=depth)+
                getNodePredecessors(g,[],[node],0,maxdepth=depth))
    h = g.subgraph(nodes)
    return h
def grabImageRegion(g, img,buffer=10):
    bb = getGraphBoundingBox(g)
    sz = img.shape
    # nodes and crds are stored in traditional (x,y,z) rather than numpy's (x,y,x)
    bs = ((max(bb[0][0]-buffer,0),min(bb[0][1]+buffer,sz[2]-1)),
          (max(bb[1][0]-buffer,0),min(bb[1][1]+buffer,sz[1]-1)),
          (max(bb[2][0]-buffer,0),min(bb[2][1]+buffer,sz[0]-1)))
          
    subimg = img[bs[2][0]:bs[2][1]+1,bs[1][0]:bs[1][1]+1,bs[0][0]:bs[0][1]+1]
    return subimg, bs

def scaleImage(img, spacing, scl = None):
    """returns an isotropic version of img, wih scaling based on voxel spacing
    provided in spcaing"""
    if( not scl ):
        ms = float(min(spacing))
        scl = [spacing[0]/ms, spacing[1]/ms, spacing[2]/ms]
        #reverse the order to match numpy's reversed indexing
    img2 = ndi.zoom(img,[scl[2],scl[1],scl[0]])
    return img2, scl
def scaleIndex(ind,scl):
    newInd = (int(ind[0]*scl[0]+0.5),int(ind[1]*scl[1]+0.5),int(ind[2]*scl[2]+0.5))
    return newInd
def scaleGraph(g, spacing, scl = None):
    """returns a scaled copy of g with scaling determined by spacing
    g: a NetworkX graph
    spacing: the voxel spacing for the associated image"""
    if( g.is_directed() ):
        h = nx.DiGraph()
    else:
        h = nx.Graph()
    
    if( not scl ):
        ms = float(min(spacing))
        scl = [spacing[0]/ms, spacing[1]/ms, spacing[2]/ms]
        
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
    return h, scl

def offsetGraph(g, offset):
    """returns an offset copy of g with the offset determined by spacing
    g: a NetworkX graph
    offset: the voxel offset to be applied"""
    if( g.is_directed() ):
        h = nx.DiGraph()
    else:
        h = nx.Graph()
        
    edges = g.edges(data = True)
    for n1,n2,data in edges:
        n1b = (n1[0]-offset[0],n1[1]-offset[1],n1[2]-offset[2])
        n2b = (n2[0]-offset[0],n2[1]-offset[1],n2[2]-offset[2])
        path = data['path']
        newPath = []
        for p in path:
            p2 = (p[0]-offset[0],p[1]-offset[1],p[2]-offset[2]) 
            newPath.append(p2)
        h.add_edge(n1b,n2b,path=newPath)
    return h    
def insertGraphInImage(g, vimg):
    

    for node in g.nodes():
        vimg[node[2],node[1],node[0]] += 2
    for edge in g.edges():
        path = g[edge[0]][edge[1]].get('path')
        if(path):
            for p in path:
                vimg[p[2],p[1],p[0]] += 1
    return vimg
def getGraphBoundingBox(g):
    crds = np.array(g.nodes())
    bbox = ((crds[:,0].min(),crds[:,0].max()),(crds[:,1].min(),crds[:,1].max()),(crds[:,2].min(),crds[:,2].max()))
    return bbox
def getCenterObject(img,node):
    """given a binary image corresponding to a graph node node, only return that
    portion of the image contiguous with node"""
    print "node to grab object for is",node
    limg = ndi.label(img)[0]
    nlabel = limg[node[2],node[1],node[0]]
    print nlabel
    
    return np.where(limg == nlabel,1,0)
def drawPath(path,view,color):
    pp = np.array(path)
    if( pp.ndim != 2 ):
        return
    if(view.lower() == 'xy'):
        p = (pp[:,1],pp[:,0])
    elif( view.lower() == 'xz'):
        p = (pp[:,2],pp[:,0])
    else:
        p = (pp[:,2], pp[:,1])
    pplot.plot(p[1],p[0],'g-',alpha=0.5)
def drawGraphEdges(g, view):
    colors = ['r','g','b','y','o','p']
    nc = len(colors)
    count = 0
    for n1, n2, edge in g.edges(data=True):
        path = [n1]+edge['path']+[n2]
        color = colors[count%nc]
        #print n1,n2
        #print "*"*20
        #print "color=%s"%color
        #print "ege length",len(edge['path'])
        #print edge['path']
        drawPath(path,view,color)
        count += 1
    #print "*"*20
    #print "*"*20

def printGraphValues(g,img, lbl=''):
    if( lbl ):
        print lbl
    for n1, n2, edge in g.edges(data=True):
        print n1, img[n1[2],n1[1],n1[0]], n2, img[n2[2],n2[1],n2[0]]
        print "edge"
        for e in edge['path']:
            print e, img[e[2],e[1],e[0]]
def visualizeXY_MPL(g,img, node, spacing, buffer=20):
    printGraphValues(g,img,"original graph and image")
    simg, bs = grabImageRegion(g, img)
    
    bso = (bs[0][0],bs[1][0],bs[2][0])
    nscl = (node[0]-bso[0],node[1]-bso[1],node[2]-bso[2])
    cimg = getCenterObject(simg,nscl)
    
    go = offsetGraph(g, bso)
    printGraphValues(go,simg, "after subimg")
    gso,scl = scaleGraph(go, spacing)
    viewImg(cimg,spacing, [1,],gso,title="")
    print bso
    print gso.nodes()
    locs = np.array(gso.nodes())
    print locs
    
    w,l = 5,3
    node_size = 10
    alpha = 0.9
    fig = pplot.figure()
    fig1 = fig.add_subplot(221,frameon=False,xticks=[],yticks=[])
    pos1 = dict(zip(gso.nodes(),zip(locs[:,0],locs[:,1])))
    pos2 = dict(zip(gso.nodes(),zip(locs[:,0],locs[:,2])))
    pos3 = dict(zip(gso.nodes(),zip(locs[:,1],locs[:,2])))
    mipz = cimg.sum(axis=0)
    pplot.gray()
    im1 = fig1.imshow(biu.win_lev(mipz, w,l))  
    nx.draw_networkx_nodes(gso,pos1,node_size=node_size, alpha=alpha)
    drawGraphEdges(gso,'xy')
    #nx.draw_networkx_edges(gso,pos1,alpha=0.5)
    
    fig2 = fig.add_subplot(222,frameon=False,xticks=[],yticks=[])
    mipy = cimg.sum(axis=1)
    pplot.gray()
    im2 = fig2.imshow(biu.win_lev(mipy, w,l))  
    nx.draw_networkx_nodes(gso,pos2,node_size=node_size, alpha=alpha)
    drawGraphEdges(gso,'xz')
    #nx.draw_networkx_edges(gso,pos2,alpha=0.5)
    
    fig3 = fig.add_subplot(223,frameon=False,xticks=[],yticks=[])
    mipx = cimg.sum(axis=2)
    pplot.gray()
    im3 = fig3.imshow(biu.win_lev(mipx, w,l))  
    nx.draw_networkx_nodes(gso,pos3,node_size=node_size, alpha=alpha)
    drawGraphEdges(gso,'yz')
    #nx.draw_networkx_edges(gso,pos3,alpha=0.5)
    fig.show()
    fig.savefig("viewxyz_%d_%d_%d.png"%node)
    #raw_input('continue')
    
def pickRandomNodeOfDegree(g,degree=3):
    import random
    d1 = [item[0] for item in g.degree().items() if item[1] == degree]
    node = random.choice(d1)
    return node
    
def main():
    #fo = file("../Skeletons/PE00000_edited_skeleton_graphs.pckle","rb")
    fo = file("PE00000_edited_bc_333_skeleton_graphs.pckle","rb")
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
    imgitk = io.readImage("PE00000.mha",returnITK=True,imgMode='sshort')
    img = itk.PyBuffer.ISS3.GetArrayFromImage(imgitk)
    spacing = imgitk.GetSpacing()
    
    #img2 = img.copy()
    #vimg = insertGraphInImage(g,img2)
    #a3d.call(data = [vimg])
    #for i in range(20):
    #    randomNode = pickRandomNodeOfDegree(g)
    #    h = getNodeSubgraph(g,randomNode)
    #    
    #    visualizeXY_MPL(h,img,buffer=20)
    fo = file("PE00000_edited_bc_333_skeleton_graphs_pruned.pckle","wb")
    cPickle.dump(g,fo)
    
def pruner(g,func):
    oldSize = g.size()
    iter = 0
    while( True ):
        func(g)
        iter += 1
        newSize = g.size()
        if( newSize == oldSize ):
            break
        else:
            oldSize = newSize
        print iter, oldSize
        
def main2():
    #fo = file("../Skeletons/PE00000_edited_skeleton_graphs_pruned.pckle","rb")
    fo = file("PE00000_edited_bc_333_skeleton_graphs_pruned.pckle","rb")
    #fo = file("PE00000_edited_bc_333_skeleton_graphs.pckle","rb")
    g = cPickle.load(fo)
    
    oldSize = g.size()
    iter = 0

    #print "drop short edges"
    #pruner(g,prune)
    #while(True):
    #    pruneTwosers(g)
    #    iter += 1
    #    newSize =  g.size()
    #    if( newSize == oldSize ):
    #        break
    #    else:
    #        oldSize = newSize
    #    print iter, oldSize
    #raw_input('continue')

    imgitk = io.readImage("PE00000_edited_bc_333.mha",returnITK=True,imgMode='sshort')
    img = itk.PyBuffer.ISS3.GetArrayFromImage(imgitk)
    spacing = imgitk.GetSpacing()
    #viewImg(img,[1,1,1], [1,],g)
    #viewImg(img,spacing, [1,])
    print "eliminate degree two nodes"
    pruner(g,pruneTwosers)
    nodes = [(94, 301, 275), (58, 221, 168),(76, 300, 183),(97, 270, 118),(341, 319, 256)]
    for i in range(20):
        randomNode = pickRandomNodeOfDegree(g)
    #for randomNode in nodes:
        print "randomly selected node is",randomNode
        h = getNodeSubgraph(g,randomNode)
        
        visualizeXY_MPL(h,img,randomNode, spacing, buffer=20)
    
if __name__ == '__main__':
    #main()
    main2()
