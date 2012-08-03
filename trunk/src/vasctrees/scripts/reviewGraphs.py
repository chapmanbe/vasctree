#!/usr/bin/env python
import vasctrees.utils as utils
import networkx as nx
import sys
import vasctrees.SkeletonGraph as sg
import vasctrees.viewGraph as viewGraph

def viewDictionary(d):
    print "in viewDictionary"
    while(True):
        keys = d.keys()
        prmpt = "Select key to display value\n" +'\t'.join(["%s"%k for k in keys])+"\nEnter to exit\n"
        key = raw_input(prmpt)
        try:
            key = eval(key)
        except:
            pass
        try:
            v = d[key]
            print type(v)
            if( type(v) is dict ):
                viewDictionary(v)
            else:
                print v
        except Exception, error:
            print error
            break
def getEdgeDepthMap(og):
    """returns the depth of each edge measured by the first node in the edge"""
    depthMap = nx.single_source_shortest_path_length(og,og.graph['root'])
    edgeDepthMap = []
    for e in og.edges():
        edgeDepthMap.append((depthMap[e[0]],(e[0],e[1])))
    edgeDepthMap.sort()
    return edgeDepthMap

def getEdgeDegrees(og):
    edges = og.edges()
    edgeDegrees = {}
    for e in edges:
        edgeDegrees[(e[0],e[1])] = (og.degree(e[0]),og.degree(e[1]))

    return edgeDegrees
def getEdgeLengths(og):
    edgeLengths = {}
    edges = og.edges(data=True)
    for e in edges:
        edgeLengths[(e[0],e[1])] = len(e[2]['path'])
    return edgeLengths

def listEdges(og):

    edgeDepthMap = getEdgeDepthMap(og)
    edgeDegrees = getEdgeDegrees(og)
    edgeLengths = getEdgeLengths(og)
    for ed in edgeDepthMap:
        print "Depth: %d; edge: %s; degrees: %s ; path length: %d"%(ed[0],ed[1],
                                                                    edgeDegrees[ed[1]],
                                                                    edgeLengths[ed[1]])

def viewEdge(og):
    while(True):
        try:
            listEdges(og)
            e1 = input("enter starting node for edge")
            e2 = input("enter ending node for edge")
            e = og.edge[e1][e2]
            viewDictionary(e)
        except KeyError:
            break
def viewNode(og):
    while(True):
        nodes = og.nodes()
        nodes.sort()
        print nodes
        try:
            n = raw_input('enter node')
            viewDictionary(n)
        except KeyError:
            break


def removeNode(og, node):
    reMap = []
    sg.safelyRemoveNode(og, node, reMap)
    sg.defineOrthogonalPlanes(og)
    sg.remapVoxelsToGraph(og, reMap)
    sg.mapPointsToPlanes(og)

def selectRemoveNodes(og):
    while(True):
        listEdges(og)

        #viewGraph.viewGraph2(og, root=og.graph['root'], fileName='', view=True)
        remove = raw_input("remove a node (yes/no)?\n")
        if( remove[0].lower() == 'y' ):
            node = input("enter 3-tuple of node label (e.g. (192,32,65))\n")
            print "you want to remove node %s. In graph %s"%(node,og.has_node(node))
            if( og.has_node(node) ):
                if( node == og.graph['root'] ):
                    print "cannot remove root node"
                    break
                if( og.degree(node) == 1 ):
                    removeNode(og,node)
                else:
                    print "can only remove degree one nodes"
        else:
            break
        
def selectAction(og ):
    mnu = """0\tView Graphs\n1\tView Edge\n2\tView Node\n3\tDelete Node\n4\tExit\n"""
    while(True):
        try:
            resp = input(mnu)
            if( resp == 0 ):
                viewGraph.viewGraph2(og, root=og.graph['root'], fileName='', view=True)
            elif( resp == 1 ):
                viewEdge(og)
            elif( resp == 2 ):
                viewNode(og)
            elif( resp == 3 ):
                selectRemoveNodes(og)
            elif( resp ==4 ):
                return
               
        except:
            print "invalid selection"



def main():
    data = utils.readGraphs(sys.argv[1])
    key = utils.getOrderedGraphKeys(data['orderedGraphs'])
    og = data['orderedGraphs'][key]
    selectAction(og )
    suffix = raw_input("suffix for saving modified file. Enter to exit without saving")
    if( suffix ):
        newKey = (key[0],key[1]+suffix)
        data['orderedGraphs'][newKey] = og
        utils.writeGraphs(data,sys.argv[1])


if __name__ == '__main__':
    main()
