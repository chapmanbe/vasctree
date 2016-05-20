#!/usr/bin/env python
import pickle
import sys
import vasctrees.viewGraph as viewGraph
import networkx as nx
import argparse
import gzip
from vasctrees.utils import readGraphs


def getKey(g):
    keys = list(g.keys())
    txt = "Select number of desired key:\n"
    for i in range(len(keys)):
        txt += """%d\t\t%s\n"""%(i,keys[i])
    while(True):
        try:
            keyNum = eval(input(txt))
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
    if( datakey in data ):
        graphClass = data[datakey]
    else:
        key = getKey(data)
        graphClass = data[key]
    if( graphkey in graphClass ):
        g = graphClass[graphkey]
    else:
        key = getKey(graphClass)
        g = graphClass[key]
    return g
def getParser():
    try:
        parser = argparse.ArgumentParser(
            description="command line processer for viewGraphs.py")
        parser.add_argument("-f", "--file", dest='fname',
                            help='name or directory for fixedImage')
        parser.add_argument("-o", "--object_number",
                            dest='objNum', type=int, default=1)
        parser.add_argument('-l', '--label', dest='label', default='')
        parser.add_argument('-s', '--surface',
                            dest='surface_display',
                            action='store_true',
                            default=False)
        parser.add_argument('-m', '--midplane',
                            dest='midplane_display',
                            action='store_true',
                            default=False)
        parser.add_argument("-u", "--unordered",
                            action='store_true', dest='view_unordered',
                            default=False)
        return parser
    except Exception as error:
        print("failed in getParser", error)
        sys.exit(0)


def getSkelGraphKeys(grphs):
    keys = list(grphs.keys())
    tmp = 'enter key for graph to view\n'
    for k in keys:
        tmp += "%s\tgraph size %d\n"%(k,nx.number_of_nodes(grphs[k]))

    while(True):
        selected_key = eval(input(tmp))
        if( selected_key in keys ):
            return selected_key

def main():
    #fo=open(sys.argv[1])
    parser = getParser()
    options = parser.parse_args()

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
        viewGraph.viewGraph2(og, root=og.graph.get('root',None), showSurface=options.surface_display, showMidPlane=options.midplane_display)
if __name__ == '__main__':
    main()
