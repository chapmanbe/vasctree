#!/usr/bin/env python
import os
from mpl_toolkits.mplot3d import axes3d,Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FixedLocator, FormatStrFormatter
import matplotlib as mpl
import matplotlib.pyplot as pp
import numpy as np

def get3DPlot(fig, og,labelNodes=False, alpha=0.05,subsample=4, verbose=True, degree = None, showSurface=True, root=None):
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
    return ax

  
def viewGraph2(og, fignum=1, labelNodes=False, alpha=0.05,subsample=4, verbose=True, degree = None, showSurface=True, root=None):
    """view an ordered graph generated using the SkeltonGraph class"""
    try:
        print "generating surface view"
        fig1 = pp.figure(fignum)
        ax1 = get3DPlot(fig1, og, labelNodes=labelNodes,alpha=alpha,subsample=subsample,verbose=verbose,degree=degree,showSurface=True,root=root)
        print "generating edge only view"
        fig2 = pp.figure(fignum+1)
        ax2 = get3DPlot(fig2, og, labelNodes=labelNodes,alpha=alpha,subsample=subsample,verbose=verbose,degree=degree,showSurface=False,root=root)
        pp.show()
    except Exception, error:
        print "failed in viewGraph2", error
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