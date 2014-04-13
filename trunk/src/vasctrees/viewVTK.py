import numpy as np
import sys
from vasctrees.utils import readGraphs
from mayavi import mlab
import random
from scipy.interpolate import griddata


class GraphViewer(object):
    def __init__(self, 
            graph = None, 
            mapping = None):
        """constructor for GraphViewer

        This function is the constructor for the GraphViewer

        graph: A NetworkX graph containing the vascular structure. If not None this has 
               precedence over fname.

        mapping: A dictionary with keys equal to edge labels and values correpsonding to color
        to draw the edge (and related items with)
        """
        self.og = graph
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

        minx = min(x)
        maxx = max(x)
        miny = min(y)
        maxy = max(y)
        minz = min(z)
        maxz = max(z)

        X,Y,Z = np.mgrid[minx:maxx:100j,miny:maxy:100j,minz:maxz:100j]

        #Visualize the points3d
        clr = (1,0,0)
        #F = griddata((x,y,z),np.ones((3,x.shape[0])),(X,Y,Z))
        pts2 = mlab.points3d(x, y, z,
                            color=(0,0,0),
                            scale_mode='none', 
                            scale_factor=0.1, 
                            opacity=0.0)
        
        # Create and visualize the mesh
        #mesh = mlab.pipeline.delaunay3d(pts2)
        #mlab.pipeline.surface(mlab.pipeline.extract_edges(mesh), color=(0,1,0),opacity=0.3, line_width=2)
        #self.surfaces = mlab.pipeline.surface(mesh,color=clr,opacity=0.1)

        #mlab.view(47, 57, 8.2, (0.1, 0.15, 0.14))
        self.figure.scene.disable_render = False
        mlab.show()

def view(graph=None, mapping = None):
    """view a SkeletonGraph with VTK

    This function creates and renders a visualization of the graph structure using VTK
    """

    gv = GraphViewer(graph=graph)
    gv.drawGraph(mapping=mapping)

