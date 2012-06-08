#!/usr/bin/env python
import cPickle
import sys
import vasctrees.viewGraph as viewGraph
import networkx as nx
import os
from mpl_toolkits.mplot3d import axes3d,Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FixedLocator, FormatStrFormatter
import matplotlib as mpl
import matplotlib.pyplot as pp
import numpy as np
import gzip
def readGraphs(fname):
    try:
        fo = gzip.open(fname,"rb")
        data = cPickle.load(fo)
        fo.close()
    except:
        fo = file(fname,"rb")
        data = cPickle.load(fo)
        fo.close()
    return data
def getKey(g):
    keys = g.keys()
    txt = "Select number of desired key:\n"
    for i in range(len(keys)):
        txt += """%d\t\t%s\n"""%(i,keys[i])
    while(True):
        try:
            keyNum = input(txt)
            if( 0 <= keyNum and keyNum < len(keys) ):
                return keys[keyNum]
        except:
            pass
    return None

def getGraphFromData(data,datakey,graphkey):
    """data  is list of standard format to be provide here later :)
    datakey is the key to the type of graph (e.g. orderedGraphs)
    graphkey is the key to the particular graph in the collection
    """
    if( data.has_key(datakey) ):
        graphClass = data[datakey]
    else:
        key = getKey(data)
        graphClass = data[key]
    if( graphClass.has_key(graphkey) ):
        g = graphClass[graphkey]
    else:
        key = getKey(graphClass)
        g = graphClass[key]
    return g

def main():
    #fo=open(sys.argv[1])
    data = readGraphs(sys.argv[1])
    num = 1 # it is always one
    datakey = sys.argv[2]
    label = sys.argv[3]
    og = getGraphFromData(data,datakey,(num,label))
    viewGraph.viewGraph2(og, root=og.graph.get('root',None))
if __name__ == '__main__':
    main()
