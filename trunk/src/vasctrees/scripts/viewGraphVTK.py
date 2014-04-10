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
import numpy as np
import sys
import argparse
from vasctrees.utils import readGraphs
from mayavi import mlab
import os
import random

os.environ['ETS_TOOLKIT'] = 'qt4'

class GraphViewer(object):
    def __init__(self, 
            graph = None, 
            fname = None, 
            objectnum = -1, 
            keyname = '',
            mapping = None):
        """constructor for GraphViewer

        This function is the constructor for the GraphViewer

        graph: A NetworkX graph containing the vascular structure. If not None this has 
               precedence over fname.

        fname: A filename containing pickled SkeletonGraph data

            objectnum: an integer from which to construct the key for fname
            keyname: a string from which to construct the key for fname

        It is assumed that the data are stored in a dictionary. The orderedGraphs are stored in
        the form data['orderedGraphs'][(objectnum,keyname)]

        mapping: A dictionary with keys equal to edge labels and values correpsonding to color
        to draw the edge (and related items with)
        """
        if graph is not None:
            self.og = graph
        elif fname is not None:
            data = readGraphs(fname)
            if( objectnum == -1 or keyname == ''):
                key = getOrderedGraphKeys(data['orderedGraphs'])
            else:
                key = (objectnum,keyname)
            self.og = data['orderedGraphs'][key]
        else:
            return
        self._setGraphData()    
    
    def _setGraphData(self):
        self.edges = self.og.edges(data=True)
        self.nodes = self.og.nodes(data=True)
        
    def _clearGraphDrawables(self):
        self.npts = 0
        self.node_points = 0
        self.surfaces = 0
        self.lines = 0
        self.crds = 0
        
    def drawGraph(self, colormap = 'jet', mapping = None):
        

        self.figure = mlab.figure(1, fgcolor=(0, 0, 0), bgcolor=(1, 1, 1))
        self.gcf = mlab.gcf()
        #mlab.clf()
        self.figure.scene.disable_render = True
        self.crds = {}
        
        # create drawables for bifurcations and endpoints
        self.narray = np.zeros((len(self.nodes),3),dtype=np.float32)
        nodeSize = np.zeros((len(self.nodes),))
        for i in range(self.narray.shape[0]):
            n = self.nodes[i]
            self.narray[i,:] =n[1]['wcrd']
            dg = self.og.degree(n[0])
            if( dg == 1 ):
                nodeSize[i] = 1.5
            else:
                nodeSize[i] = 0.5
        self.npts = mlab.points3d( self.narray[:,0],
                                   self.narray[:,1],
                                   self.narray[:,2], 
                                   nodeSize,
                                   colormap="jet", 
                                   scale_factor=4.0)
        lut = self.npts.module_manager.scalar_lut_manager.lut.table.to_array()
        if mapping is None:
            mapping = {}
            for e in self.edges:
                clr = lut[random.randint(0,255)]
                clr = (clr[0]/255.0,clr[1]/255.0,clr[2]/255.0)
                mapping[(e[0],e[1])] = clr

        self.node_points = self.npts.glyph.glyph_source.glyph_source.output.points.to_array()
        
        # now draw
        
        self.lines = {}
        colors = ((1,0,0),(0,1,0),(0,0,1),(1,1,0),(1,0,1),(0,1,1))
        surface = None
        for e in self.edges:
            try:
                #clr = colors[counter%len(colors)]
                mp = e[2]["mappedPoints"]
                x = mp[::4,0]
                y = mp[::4,1]
                z = mp[::4,2]
                clr = mapping[(e[0],e[1])]
                #Visualize the points
                pts = mlab.points3d(x, y, z, 
                                    color=clr,
                                    scale_mode='none', 
                                    scale_factor=0.3, 
                                    opacity=0.5)
                if surface is None:
                    surface = e[2]['mappedPoints']
                else:
                    try:
                        surface = np.concatenate((surface,mp),axis=0)
                    except ValueError:
                        pass
                sp = e[2]['d0']
                
                #sys.stderr = self.stderr
                pts = 0
                if( sp ):
                    self.lines[(e[0],e[1])] = mlab.plot3d(sp[0],sp[1],sp[2],
                                                        color=clr, 
                                                        tube_radius=1.0)
            except KeyError, error:
                print "KeyError", error
            except IndexError, error:
                print "IndexError", error

        x = surface[::4,0]
        y = surface[::4,1]
        z = surface[::4,2]
        #Visualize the points
        #pts = mlab.points3d(x, y, z, 
        #                    color=clr,
        #                    scale_mode='none', 
        #                    scale_factor=0.3, 
        #                    opacity=0.5)
        
        # Create and visualize the mesh
        #mesh = mlab.pipeline.delaunay3d(pts)
        #mlab.pipeline.surface(mlab.pipeline.extract_edges(mesh), color=clr,opacity=0.3, line_width=2)
        #self.surfaces = mlab.pipeline.surface(mesh,color=(1,1,1),opacity=0.0)

        #mlab.view(47, 57, 8.2, (0.1, 0.15, 0.14))
        self.figure.scene.disable_render = False
        mlab.show()


def getOrderedGraphKeys(ogs):
    keys = ogs.keys()
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
def getParser():
    try:
        parser = argparse.ArgumentParser(description="command line parser for editGraph.py")
        parser.add_argument("-f","--file",dest='fname',
                          help='name or directory for fixedImage')
        parser.add_argument("-o","--object_number",dest='objNum',type=int,default=-1)
        parser.add_argument('-l','--label',dest='label',default='')

        return parser
    except Exception, error:
        print "failed in getParser", error  
        sys.exit(0)               

def view(graph=None, filename = None, objectnum = -1,
        keyname = "", mapping = None):
    """view a SkeletonGraph with VTK

    This function creates and renders a visualization of the graph structure using VTK
    """

    gv = GraphViewer(graph=graph, fname=filename, 
                     objectnum = options.objNum, keyname=options.label,
                     mapping = mapping)
    gv.drawGraph()

if __name__ == '__main__':
    parser = getParser()
    options = parser.parse_args()
    view(filename=options.fname, objectnum = options.objNum, keyname=options.label)
    
