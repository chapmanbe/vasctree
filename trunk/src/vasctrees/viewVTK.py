import numpy as np
# import sys
# from vasctrees.utils import readGraphs
from mayavi import mlab
import random
import math
import os
# from scipy.interpolate import griddata


class GraphViewer(object):

    def __init__(self,
                 graph=None,
                 mapping=None,
                 attribute=None,
                 title="Plot",
                 root=None,
                 showAxes=False):
        """constructor for GraphViewer

        This function is the constructor for the GraphViewer

        graph: A NetworkX graph containing the vascular structure. If not None this has
               precedence over fname.

        mapping: A dictionary with keys equal to edge labels and values correpsonding to color
        to draw the edge (and related items with)
        """
        self.og = graph
        self._setGraphData()
        self.attribute = attribute
        self.title = title
        self._setRoot(root)
        self.showAxes = showAxes

    def _setGraphData(self):
        self.edges = self.og.edges(data=True)
        self.nodes = self.og.nodes(data=True)

    def _clearGraphDrawables(self):
        self.npts = 0
        self.node_points = 0
        self.surfaces = 0
        self.lines = 0
        self.crds = 0

    def _setRoot(self, root):
        try:
            index = self.og.nodes().index(root)
            self.root = self.root
            self.root_wcrd = tuple(map(int, self.og.nodes(data=True)[index][1]['wcrd']))
        except:
            # find root node
            e1 = []
            e0 = []
            for e in self.og.edges():
                e1.append(e[1])
                e0.append(e[0])
            es = [v for v in e0 if v not in e1]
            self.root = es.pop()
            index = self.og.nodes().index(self.root)
            self.root_wcrd = tuple(map(int, self.og.nodes(data=True)[index][1]['wcrd']))

    def drawGraph(self, colormap='jet', mapping=None, surfaceOnly=False):
        """
        """
        self.figure = mlab.figure(1, fgcolor=(0, 0, 0), bgcolor=(1, 1, 1), size=(1200, 900))
        self.gcf = mlab.gcf()
        # mlab.clf()
        self.figure.scene.disable_render = True
        self.crds = {}
        print self.root_wcrd, self.root

        # create drawables for bifurcations and endpoints
        self.narray = np.zeros((len(self.nodes), 3), dtype=np.float32)
        nodeSize = np.zeros((len(self.nodes),))
        labels = []
        for i in range(self.narray.shape[0]):
            n = self.nodes[i]
            self.narray[i, :] = n[1]['wcrd']
            dg = self.og.degree(n[0])
            if(dg == 1):
                tmp = (self.narray[i, 0], self.narray[i, 1], self.narray[i, 2])
                nodeSize[i] = 1 if tuple(map(int, tmp)) != self.root_wcrd else 1.5
                labels.append((n[0], tmp))
            else:
                nodeSize[i] = 0.5

        # # create random mapping
        if mapping is None:
            mapping = {}
            for e in self.edges:
                clr = random.randint(0, 1)
                mapping[(e[0], e[1])] = clr


        # now draw
        self.lines = {}
        surface = None
        self.surfaces = None
        x = np.array([0, 0])
        y = np.array([0, 0])
        z = np.array([0, 0])
        s = np.array([0, 4])
        for e in self.edges:
            try:
                mp = e[2]["mappedPoints"]
                x = np.concatenate((x, mp[::1, 0]))
                y = np.concatenate((y, mp[::1, 1]))
                z = np.concatenate((z, mp[::1, 2]))
                clr = mapping[(e[0], e[1])]
                # clr_t = clr, clr, clr
                s = np.concatenate((s, np.linspace(clr, clr, len(mp[::1, 0]))))
                print clr
                if surface is None:
                    surface = e[2]['mappedPoints']
                else:
                    try:
                        surface = np.concatenate((surface, mp), axis=0)
                    except ValueError:
                        pass
                sp = e[2]['d0']
                if(sp):
                    if not surfaceOnly:
                        self.lines[(e[0], e[1])] = mlab.plot3d(sp[0],
                                                               sp[1],
                                                               sp[2],
                                                               color=(0, 0, 0),
                                                               # color=clrt,
                                                               tube_radius=.3)
            except KeyError, error:
                print "KeyError", error
            except IndexError, error:
                print "IndexError", error

        print x.shape
        print y.shape
        print z.shape
        print s.shape
        self.surfaces = mlab.points3d(x, y, z, s,
                                      # colormap="Greys",
                                      colormap="jet",
                                      scale_mode='none',
                                      scale_factor=.4,
                                      opacity=0.5)

        if not surfaceOnly:
            self.npts = mlab.points3d(self.narray[:, 0],
                                      self.narray[:, 1],
                                      self.narray[:, 2],
                                      nodeSize,
                                      colormap="jet",
                                      scale_factor=4.0)

        x = surface[::1, 0]
        y = surface[::1, 1]
        z = surface[::1, 2]

        minx = min(x)
        maxx = max(x)
        miny = min(y)
        maxy = max(y)
        minz = min(z)
        maxz = max(z)

        X, Y, Z = np.mgrid[minx:maxx:100j, miny:maxy:100j, minz:maxz:100j]

        # Visualize the points3d
        clr = (1, 0, 0)

        # Labels and legends
        if(self.showAxes):
            mlab.xlabel("x")
            mlab.ylabel("y")
            mlab.xlabel("z")

        mlab.title(self.title, size=.5, height=.90)
        for label in labels:
            l = label[1]
            fl = tuple(map(int, l))
            if fl == self.root_wcrd:
                mlab.text(l[0], l[1], repr(label[0]) + " (root)", z=l[2], width=.2, color=(0, 0, 0))
            else:
                mlab.text(l[0], l[1], repr(label[0]), z=l[2], width=.15, color=(0, 0, 0))

        #adjust lut transparency
        lut = self.surfaces.module_manager.scalar_lut_manager.lut.table.to_array()
        lut[:, -1] = np.linspace(110, 110, 256)
        self.surfaces.module_manager.scalar_lut_manager.lut.table = lut

        # add scale bar
        if self.surfaces is not None:
            mlab.scalarbar(title="scale", orientation='vertical', nb_labels=5)

        self.figure.scene.disable_render = False
        mlab.view(0, 180, 400, roll=180)

        saveFileName = os.path.join(os.path.expanduser("~"), "desktop", self.title + ".png")
        mlab.savefig(saveFileName)
        mlab.close()
        # mlab.show()

        # arr = mlab.screenshot()
        # print arr
        # import pylab as pl
        # pl.imshow(arr)
        # pl.axis('off')
        # pl.show()


def view(graph=None, mapping=None, title="Plot", surfaceOnly=False, root=None):
    """view a SkeletonGraph with VTK

    This function creates and renders a visualization of the graph structure using VTK

    graph: a networkx digraph
    mapping: a color mapping dictionary with edge tuple as key and measure from zero to one as the value
    surfaceOnly: bool specifying to plot only the surface and not the lines and nodes
    root: the root node of the digraph
    """

    gv = GraphViewer(graph=graph, title=title, root=root, showAxes=False)
    gv.drawGraph(mapping=mapping, surfaceOnly=surfaceOnly)
