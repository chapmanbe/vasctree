#!/usr/bin/env python
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator
#import matplotlib as mpl_connect
import matplotlib.colors as colors
import matplotlib.pyplot as pp
import numpy as np
import networkx as nx
def get3DPlotUndirected(fig, og,
        verbose=True, degree = None):

    ax = Axes3D(fig)
    nodes = og.nodes(data=True)
    ends = []
    paths = []
    bifurs = []
    axes = ax.get_axes()
    axes.set_axis_off()
    ax.set_axes(axes)

    for i in range(len(nodes)):
        dg = og.degree(nodes[i][0])
        if( dg == 1 ):
            ends.append(nodes[i][0])
        elif( dg == 2 ):
            paths.append(nodes[i][0])
        else:
            bifurs.append(nodes[i][0])

    earray = np.array(ends)
    parray = np.array(paths)
    barray = np.array(bifurs)
    colors = ['r','g','b','y','m','c']
    counter = 0

    ax.scatter(earray[:,0],earray[:,1],earray[:,2],color='r',marker='o',linewidth=3, picker=5)
    ax.scatter(parray[:,0],parray[:,1],parray[:,2],color='g',marker='o',linewidth=1, picker=5)
    ax.scatter(barray[:,0],barray[:,1],barray[:,2],color='b',marker='o',linewidth=8, picker=5)



    ax.w_zaxis.set_major_locator(LinearLocator(3))
    ax.w_xaxis.set_major_locator(LinearLocator(3))
    ax.w_yaxis.set_major_locator(LinearLocator(3))
    return ax

def getGraphWithMapping(fig, og, mapping, alpha=0.05,subsample=4,
              degree = None, showSurface=True,
              root=None,
              colormap = 'jet'):
    ax = Axes3D(fig)
    edges = og.edges(data=True)
    nodes = og.nodes(data=True)
    narray = np.zeros((len(nodes),3),np.float32)
    axes = ax.get_axes()
    axes.set_axis_off()
    ax.set_axes(axes)
    pp.set_cmap(colormap)
    vmax = np.max(mapping.values())
    vmin = np.min(mapping.values())
    cNorm = colors.Normalize(vmin=vmin,vmax=vmax)
    scalarMap = cm.ScalarMappable(norm=cNorm,cmap=pp.get_cmap(colormap))
    if( root ):
        rcrd = og.node[root]["wcrd"]
        ax.text(rcrd[0],rcrd[1],root[2],"Root")
    ss = 4
    for e in edges:
        try:
            sp = e[2]['d0']
            mps = e[2]['mappedPoints']
            clr = scalarMap.to_rgba(mapping[(e[0],e[1])])
            print "%s with mapping %s maps to color %s"%((e[0],e[1]),mapping[(e[0],e[1])],clr)
            ax.plot(sp[0],sp[1],sp[2],color = clr)
            if showSurface :
                try:
                    ax.scatter(mps[::ss,0],mps[::ss,1],mps[::ss,2],color = clr,marker='+',alpha=alpha)
                except Exception:
                    pass

        except KeyError:
            print "cannot plot edge (%s,%s)"%(e[0],e[1])
        except TypeError:
            if( e[2]['d0'] == None ):
                print "No fitted data for edge (%s,%s)"%(e[0],e[1])

    ax.scatter(narray[:,0],narray[:,1],narray[:,2],color='k',marker='o',linewidth=3, picker=5)
    ax.scatter([rcrd[0]],[rcrd[1]],[rcrd[2]],color='r',marker='o',linewidth=10,picker=5)

    ax.w_zaxis.set_major_locator(LinearLocator(3))
    ax.w_xaxis.set_major_locator(LinearLocator(3))
    ax.w_yaxis.set_major_locator(LinearLocator(3))
    return ax

def get3DPlot(fig, og,labelNodes=False, alpha=0.05,subsample=4,
              verbose=True, degree = None, showSurface=True,
              showMidPlane=True, root=None):
    ax = Axes3D(fig)
    edges = og.edges(data=True)
    nodes = og.nodes(data=True)
    narray = np.zeros((len(nodes),3),np.float32)
    axes = ax.get_axes()
    axes.set_axis_off()
    ax.set_axes(axes)

    for i in range(len(nodes)):
        narray[i,:] = nodes[i][1]['wcrd']
        dg = og.degree(nodes[i][0])
        if( labelNodes and (degree == None or dg == degree)):
            ax.text(narray[i,0],narray[i,1],narray[i,2],"(%d,%d,%d)"%(nodes[i][0][0],nodes[i][0][1],nodes[i][0][2]))
    print("root is",root)
    if root:
        rcrd = og.node[root]["wcrd"]
        ax.text(rcrd[0],rcrd[1],root[2],"Root")
    colors = ['r','g','b','y','m','c']
    counter = 0
    ss = 4
    for e in edges:
        try:
            sp = e[2]['d0']
            mps = e[2]['mappedPoints']
            clr = colors[counter%len(colors)]
            ax.plot(sp[0],sp[1],sp[2],color = clr)
            if showSurface:
                try:
                    ax.scatter(mps[::ss,0],mps[::ss,1],mps[::ss,2],color = clr,marker='+',alpha=0.05)
                except Exception, error:
                    print("couldn't plot surface for edge (%s,%s). Surface points shape is %s. Error is %s"%\
                    (e[0],e[1],mps.shape,error))
            if showMidPlane:
                try:
                    planePoints = e[2]['planePoints']
                    midpoint = len(planePoints.keys())/2
                    mps = np.array(e[2]['planePoints'][midpoint])

                    ax.scatter(mps[:,0],mps[:,1],mps[:,2],color = clr,marker='+',alpha=0.5)
                except Exception, error:
                    print("couldn't plot midplane points for edge (%s,%s). Plane points shape is %s. Error is %s"%\
                    (e[0],e[1],mps.shape,error))

            counter += 1
        except KeyError:
            print "cannot plot edge (%s,%s)"%(e[0],e[1])
        except TypeError:
            if( e[2]['d0'] == None ):
                print "No fitted data for edge (%s,%s)"%(e[0],e[1])

    ax.scatter(narray[:,0],narray[:,1],narray[:,2],color='k',marker='o',linewidth=3, picker=5)
    ax.scatter([rcrd[0]],[rcrd[1]],[rcrd[2]],color='r',marker='o',linewidth=10,picker=5)



    ax.w_zaxis.set_major_locator(LinearLocator(3))
    ax.w_xaxis.set_major_locator(LinearLocator(3))
    ax.w_yaxis.set_major_locator(LinearLocator(3))
    return ax

def get3DPlotAnatomy(fig, og,labelNodes=False, alpha=0.05,subsample=4,
              verbose=True, degree = None, showSurface=True,
              showMidPlane=True, root=None):
    ax = Axes3D(fig)
    edges = og.edges(data=True)
    nodes = og.nodes(data=True)
    narray = np.zeros((len(nodes),3),np.float32)
    axes = ax.get_axes()
    axes.set_axis_off()
    ax.set_axes(axes)

    for i in range(len(nodes)):
        narray[i,:] = nodes[i][1]['wcrd']
        dg = og.degree(nodes[i][0])
        if( labelNodes and (degree == None or dg == degree)):
            ax.text(narray[i,0],narray[i,1],narray[i,2],"(%d,%d,%d)"%(nodes[i][0][0],nodes[i][0][1],nodes[i][0][2]))
    print "root is",root
    if( root ):
        rcrd = og.node[root]["wcrd"]
        ax.text(rcrd[0],rcrd[1],root[2],"Root")
    colors = ['r','g','b','y','m','c']
    counter = 0
    ss = 4
    for e in edges:
        try:
            sp = e[2]['d0']
            mps = e[2]['mappedPoints']
            edgeDepth = nx.shortest_path_length(og,root,e[1])
            if edgeDepth == 1:
                clr = 'r'
            elif edgeDepth == 2:
                clr = 'g'
            else:
                clr = 'b'
            ax.plot(sp[0],sp[1],sp[2],color = clr)
            if( showSurface):
                try:
                    ax.scatter(mps[::ss,0],mps[::ss,1],mps[::ss,2],color = clr,marker='+',alpha=0.05)
                except Exception, error:
                    print "couldn't plot surface for edge (%s,%s). Surface points shape is %s. Error is %s"%\
                    (e[0],e[1],mps.shape,error)
            if( showMidPlane ):
                try:
                    planePoints = e[2]['planePoints']
                    midpoint = len(planePoints.keys())/2
                    mps = np.array(e[2]['planePoints'][midpoint])

                    ax.scatter(mps[:,0],mps[:,1],mps[:,2],color = clr,marker='+',alpha=0.5)
                except Exception, error:
                    print "couldn't plot midplane points for edge (%s,%s). Plane points shape is %s. Error is %s"%\
                    (e[0],e[1],mps.shape,error)

            counter += 1
        except KeyError:
            print "cannot plot edge (%s,%s)"%(e[0],e[1])
        except TypeError:
            if( e[2]['d0'] == None ):
                print "No fitted data for edge (%s,%s)"%(e[0],e[1])

    ax.scatter(narray[:,0],narray[:,1],narray[:,2],color='k',marker='o',linewidth=3, picker=5)
    ax.scatter([rcrd[0]],[rcrd[1]],[rcrd[2]],color='r',marker='o',linewidth=10,picker=5)



    ax.w_zaxis.set_major_locator(LinearLocator(3))
    ax.w_xaxis.set_major_locator(LinearLocator(3))
    ax.w_yaxis.set_major_locator(LinearLocator(3))
    return ax

def onclick(event):
    print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(
        event.button, event.x, event.y, event.xdata, event.ydata)
def onpick(event):
    print event.artist
    if event.artist!='line': return True

    N = len(event.ind)
    if not N: return True


    for subplotnum, dataind in enumerate(event.ind):
        print subplotnum, dataind
    return True
def viewUndirectedGraph(og, fignum=1, subsample=4, verbose=True,
        degree = None, fileName = None, view=True ):
    """view an ordered graph generated using the SkeltonGraph class"""
    fig1 = pp.figure(fignum)
    ax1 = get3DPlotUndirected(fig1, og, verbose=verbose,degree=degree)
    if( fileName ):
        fig1.savefig(fileName+"_undirected.fig1.png")
    fig1.canvas.mpl_connect('pick_event', onpick)
    if( view ):
        pp.show()
def viewSurfaceGraph(og, fignum=1, labelNodes=False, alpha=0.05,subsample=4, verbose=True,
        degree = None, root=None, fileName = None, view=True,theta=100,phi= 120):
    """view an ordered graph generated using the SkeltonGraph class"""
    print "generating surface view"
    fig1 = pp.figure(fignum)
    ax1 = get3DPlot(fig1, og, labelNodes=labelNodes,
                    alpha=alpha,subsample=subsample,
                    verbose=verbose,degree=degree,
                    showSurface=True,showMidPlane=False,root=root)
    ax1.view_init(theta,phi)
    if( fileName ):
        fig1.savefig(fileName+".surface_fig.png")

    if( view ):
        pp.show()

def viewGraphWithMapping(og, mapping, fignum=1,  alpha=0.05,subsample=4,
				colormap='jet', verbose=True,
        degree = None, showSurface=True, root=None, fileName = None,
        view=True,theta=100,phi= 120):
    """view an ordered graph generated using the SkeltonGraph class"""
    fig1 = pp.figure(fignum)
    ax1 = getGraphWithMapping(fig1, og, mapping, alpha=alpha, subsample=subsample,
                              degree=degree, showSurface=showSurface,root=root,
                              colormap=colormap)
    ax1.view_init(theta,phi)
    if( fileName ):
        fig1.savefig(fileName+".mapping.png")
    if( view ):
        pp.show()

def viewGraph0(og, fignum=1, labelNodes=False, alpha=0.05,subsample=4, verbose=True,
        degree = None, showSurface=True, root=None, fileName = None, view=True,theta=100,phi= 120):
    """view an ordered graph generated using the SkeltonGraph class"""
    print "generating surface view"
    fig1 = pp.figure(fignum)
    ax1 = get3DPlot(fig1, og, labelNodes=labelNodes,alpha=alpha,subsample=subsample,
                    verbose=verbose,degree=degree,
                    showSurface=showSurface,showMidPlane=False,root=root)
    ax1.view_init(theta,phi)
    print "generating edge only view"
    if( fileName ):
        fig1.savefig(fileName+".fig1.png")
    if( view ):
        pp.show()

    pp.close(fig1)

def viewGraph2(og, fignum=1, labelNodes=False, alpha=0.05,subsample=4,
              verbose=True, degree = None, showSurface=True, showMidPlane=True,
              root=None, fileName = None, view=True,theta=100,phi= 120):
    """view an ordered graph generated using the SkeltonGraph class"""
    print("generating surface view")
    fig1 = pp.figure(fignum)
    ax1 = get3DPlot(fig1, og, labelNodes=labelNodes,alpha=alpha,
                              subsample=subsample,verbose=verbose,
                              degree=degree,showSurface=showSurface,
                              showMidPlane=False,root=root)
    ax1.view_init(theta,phi)
    print("generating edge only view")
    if fileName:
        fig1.savefig(fileName+".fig1.png")
    fig2 = pp.figure(fignum+1)
    ax2 = get3DPlot(fig2, og, labelNodes=labelNodes,alpha=alpha,subsample=subsample,verbose=verbose,degree=degree,showSurface=False,showMidPlane=showMidPlane,root=root)
    ax2.view_init(theta,phi)
    #cid = fig2.canvas.mpl_connect('button_press_event', onclick)
    fig2.canvas.mpl_connect('pick_event', onpick)
    if fileName:
        fig2.savefig(fileName+".fig2.png")
    if view:
        pp.show()
def viewGraph1(og, fignum=1, labelNodes=False, alpha=0.05,subsample=4, verbose=True, degree = None, showSurface=True, root=None):
    """view an ordered graph generated using the SkeltonGraph class"""
    if( verbose ):
        print "viewing graph"
    edges = og.edges(data=True)
    nodes = og.nodes(data=True)
    narray = np.zeros((len(nodes),3),np.float32)

    fig1 = pp.figure(fignum)
    ax = Axes3D(fig1)

    axes = ax.get_axes()
    axes.set_axis_off()
    ax.set_axes(axes)

    for i in range(len(nodes)):
        narray[i,:] = nodes[i][1]['wcrd']
        dg = og.degree(nodes[i][0])
        if( labelNodes and (degree == None or dg == degree)):
            ax.text(narray[i,0],narray[i,1],narray[i,2],"(%d,%d,%d)"%(nodes[i][0][0],nodes[i][0][1],nodes[i][0][2]))
    print "root is",root
    if( root ):
        rcrd = og.node[root]["wcrd"]
        ax.text(rcrd[0],rcrd[1],root[2],"Root")
    colors = ['r','g','b','y','m','c']
    counter = 0
    ss = 4
    for e in edges:
        sp = e[2]['d0']
        mps = e[2]['mappedPoints']
        clr = colors[counter%len(colors)]
        ax.plot(sp[0],sp[1],sp[2],color = clr)
        if( showSurface):
            try:
                ax.scatter(mps[::ss,0],mps[::ss,1],mps[::ss,2],color = clr,marker='+',alpha=0.05)
            except Exception, error:
                print "couldn't plot surface for edge (%s,%s). Surface points shape is %s. Error is %s"%\
                (e[0],e[1],mps.shape,error)
        counter += 1

    ax.scatter(narray[:,0],narray[:,1],narray[:,2],color='k',marker='o',linewidth=3)



    ax.w_zaxis.set_major_locator(LinearLocator(3))
    ax.w_xaxis.set_major_locator(LinearLocator(3))
    ax.w_yaxis.set_major_locator(LinearLocator(3))
    pp.show()

def viewGraphWithMidPlane(og, fignum=1, labelNodes=False, alpha=0.05,subsample=4, verbose=True, degree = None, showMidPlane=True, root=None):
    """view an ordered graph generated using the SkeltonGraph class"""
    if( verbose ):
        print "viewing graph"
    edges = og.edges(data=True)
    nodes = og.nodes(data=True)
    narray = np.zeros((len(nodes),3),np.float32)

    fig1 = pp.figure(fignum)
    ax = Axes3D(fig1)

    axes = ax.get_axes()
    axes.set_axis_off()
    ax.set_axes(axes)

    for i in range(len(nodes)):
        narray[i,:] = nodes[i][1]['wcrd']
        dg = og.degree(nodes[i][0])
        if( labelNodes and (degree == None or dg == degree)):
            ax.text(narray[i,0],narray[i,1],narray[i,2],"(%d,%d,%d)"%(nodes[i][0][0],nodes[i][0][1],nodes[i][0][2]))
    print "root is",root
    if( root ):
        rcrd = og.node[root]["wcrd"]
        ax.text(rcrd[0],rcrd[1],root[2],"Root")
    colors = ['r','g','b','y','m','c']
    counter = 0
    ss = 4
    for e in edges:
        sp = e[2]['d0']
        pp = e[2]['planePoints']
        clr = colors[counter%len(colors)]
        ax.plot(sp[0],sp[1],sp[2],color = clr)
        if( showMidPlane ):
            midpoint = len(pp.keys())/2
            mps = e[2]['planePoints'][midpoint]
            try:
                ax.scatter(mps[::ss,0],mps[::ss,1],mps[::ss,2],color = clr,marker='+',alpha=0.05)
            except Exception, error:
                print "couldn't plot surface for edge (%s,%s). Surface points shape is %s. Error is %s"%\
                (e[0],e[1],mps.shape,error)
        counter += 1

    ax.scatter(narray[:,0],narray[:,1],narray[:,2],color='k',marker='o',linewidth=3)



    ax.w_zaxis.set_major_locator(LinearLocator(3))
    ax.w_xaxis.set_major_locator(LinearLocator(3))
    ax.w_yaxis.set_major_locator(LinearLocator(3))
    pp.show()
