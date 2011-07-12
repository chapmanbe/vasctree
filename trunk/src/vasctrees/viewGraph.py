#!/usr/bin/env python
import os
from mpl_toolkits.mplot3d import axes3d,Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FixedLocator, FormatStrFormatter
import matplotlib as mpl
import matplotlib.pyplot as pp
import numpy as np

def viewGraph1(og, fignum=1, labelNodes=False, alpha=0.05,subsample=4):
    """view an ordered graph generated using the SkeltonGraph class"""
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
        if( labelNodes ):
            ax.text(narray[i,0],narray[i,1],narray[i,2],"(%d,%d,%d)"%(nodes[i][0][0],nodes[i][0][1],nodes[i][0][2]))
    colors = ['r','g','b','y','m','c']
    counter = 0
    ss = 4
    for e in edges:
        sp = e[2]['d0']
        mps = e[2]['mappedPoints']
        clr = colors[counter%len(colors)]
        ax.plot(sp[0],sp[1],sp[2],color = clr)
        ax.scatter(mps[::ss,0],mps[::ss,1],mps[::ss,2],color = clr,marker='+',alpha=0.05)
        counter += 1
            
    ax.scatter(narray[:,0],narray[:,1],narray[:,2],color='k',marker='o',linewidth=3)
        
    
    
    ax.w_zaxis.set_major_locator(LinearLocator(3))
    ax.w_xaxis.set_major_locator(LinearLocator(3))
    ax.w_yaxis.set_major_locator(LinearLocator(3))
    pp.show()