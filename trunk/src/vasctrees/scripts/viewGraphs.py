#!/usr/bin/env python
import cPickle
import sys
import vasctrees.viewGraph as viewGraph
import networkx as nx
import os
import sys
from optparse import OptionParser
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
def getParser():
    try:
        parser = OptionParser()
        parser.add_option("-f","--file",dest='fname',
                          help='name or directory for fixedImage')
        parser.add_option("-o","--object_number",dest='objNum',type='int',default='-1')
        parser.add_option('-l','--label',dest='label',default='')
        parser.add_option("-u","--unordered",action='store_true', dest='view_unordered',
                default=False) 


        return parser
    except Exception, error:
        print "failed in getParser", error  
        sys.exit(0)
def getSkelGraphKeys(grphs):
    keys = grphs.keys()
    tmp = 'enter key for graph to view\n'
    for k in keys:
        tmp += "%s\tgraph size %d\n"%(k,nx.number_of_nodes(grphs[k]))

    while(True):
        selected_key = input(tmp)
        if( selected_key in keys ):
            return selected_key

def main():
    #fo=open(sys.argv[1])
    parser = getParser()
    (options, args) = parser.parse_args()

    data = readGraphs(options.fname)
    if( options.view_unordered ):
        datakey = "skelGraphs"
        graphKey = getSkelGraphKeys(data[datakey])
        viewGraph.viewUndirectedGraph(data[datakey][graphKey])
    else:
        datakey = "orderedGraphs"
        label = options.label
        num = options.objNum
        og = getGraphFromData(data,datakey,(num,label))
        viewGraph.viewGraph2(og, root=og.graph.get('root',None))
if __name__ == '__main__':
    main()
