#!/usr/bin/env python
"""A simple class for viewing and editing the directed graphs generated with a
SkeletonGraph object. Relies on mayavi/vtk for the visuzalization. My understanding of
the mayavi interface is quiet limited. Program will occassionally freeze for no
apparent reason.

The program is run as a script with three arguments:
skeleton-graph-file ob

skeleton-graph-file: a pickle file generated with a SkeletonGraph save
object-number The object number from which the graphs were generated.
(this refers to the sequence of labeled-objects used to generated the graph
and is the integer in the tuple-key used in SkeletonGraph object)

graph-key the string label associated with the graph.

If the graph is modified, a new graph is added to the SkeletonGraph object with
a graph-key equal to the specified graph-key concatenated with '_edited'"""
import sys
import argparse
import vasctrees.utils as utils
import os

os.environ['ETS_TOOLKIT'] = 'qt4'

import vasctrees.viewVTK as viewVTK

def getParser():
    try:
        parser = argparse.ArgumentParser(description="command line parser for editGraph.py")
        parser.add_argument("-f","--file",dest='fname',
                          help='name or directory for fixedImage')
        parser.add_argument("-o","--object_number",dest='objNum',type=int,default=-1)
        parser.add_argument('-l','--label',dest='label',default='')

        return parser
    except Exception as error:
        print("failed in getParser", error)  
        sys.exit(0)               


if __name__ == '__main__':
    parser = getParser()
    options = parser.parse_args()
    if options.fname is not None:
        data = utils.readGraphs(options.fname)
        if( options.objNum == -1 or options.label == ''):
            key = utils.getOrderedGraphKeys(data['orderedGraphs'])
        else:
            key = (options.objNum,options.label)
        og = data['orderedGraphs'][key]
        viewVTK.view(graph=og)
    else:
        pass
