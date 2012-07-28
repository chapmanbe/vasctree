#!/usr/bin/env python
"""A simple class for viewing and editing the directed graphs generated with a
SkeletonGraph object. Relies on mayavi/vtk for the visuzalization. My understanding of
the mayavi interface is quiet limited. Program will occassionally freeze for no
apparent reason.

The program is run as a script with three arguments:
skeleton-graph-file object-number graph-key

skeleton-graph-file: a pickle file generated with a SkeletonGraph save
object-number The object number from which the graphs were generated.
(this refers to the sequence of labeled-objects used to generated the graph
and is the integer in the tuple-key used in SkeletonGraph object)

graph-key the string label associated with the graph.

If the graph is modified, a new graph is added to the SkeletonGraph object with
a graph-key equal to the specified graph-key concatenated with '_edited'"""
import cPickle
import numpy as np
import sys
from optparse import OptionParser
from vasctrees.SkeletonGraph import SkeletonGraph
from mayavi import mlab
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

class GraphViewer(object):
    def __init__(self,fname, objectnum = -1, keyname = ''):
        self.fname = fname
        #self.efile = file(fname+".error","w")
        #self.stderr = sys.stderr
        #f = file(fname)
        #self.data = cPickle.load(f)
        self.data = readGraphs(fname)
        #f.close()
        if( objectnum == -1 or keyname == ''):
            self.key = getOrderedGraphKeys(self.data['orderedGraphs'])
        else:
            self.key = (objectnum,keyname)
        self.sg = SkeletonGraph()
        self.sg.orderedGraphs = self.data['orderedGraphs']
        self.sg.roots = self.data['roots']
        if(not self.sg.orderedGraphs[self.key].graph.has_key("root")):
            self.sg.orderedGraphs[self.key].graph["root"] = self.sg.roots[self.key]

        #self.picker = self.figure.scene.get()['picker']
        #self.figure.scene.picker.pointpicker.add_observer('EndPickEvent',self.picker_callback)
        self._setGraphData()    
        # Decrease the tolerance, so that we can more easily select a precise
        # point.
        self.editnum = 1
        # create a new key and copy of graph
        newKey = (self.key[0],"%s_edited"%(self.key[1],))
        self.sg.orderedGraphs[newKey] = self.sg.orderedGraphs[self.key].copy()
        self.key = newKey
        self.deleteNode = None
    
    def saveModifiedData(self):
        print "saving modified data"
        self.data['orderedGraphs'] = self.sg.orderedGraphs
        #f = file(self.fname,"wb")
        f = gzip.open(self.fname,"wb")
        cPickle.dump(self.data,f)
        f.close()
    def _setGraphData(self):
        self.og = self.sg.orderedGraphs[self.key]
        self.edges = self.og.edges(data=True)
        self.nodes = self.og.nodes(data=True)
        
    def _clearGraphDrawables(self):
        self.npts = 0
        self.node_points = 0
        self.surfaces = 0
        self.lines = 0
        self.crds = 0
        
    def drawGraph(self):
        self.figure = mlab.figure(self.editnum, fgcolor=(0, 0, 0), bgcolor=(1, 1, 1))
        self.gcf = mlab.gcf()
        #mlab.clf()
        self.picker = self.figure.on_mouse_pick(self.picker_callback)
        self.picker.tolerance = 0.01
        self.figure.scene.disable_render = True
        #self.gcf.scene.picker.pointpicker.add_observer("EndPickEvent",self.picker_callback)
        node_color = []
        self.crds = {}
        
        # create drawables for bifurcations and endpoints
        self.narray = np.zeros((len(self.nodes),3),dtype=np.float32)
        s = np.zeros((len(self.nodes),))
        for i in range(self.narray.shape[0]):
            n = self.nodes[i]
            self.narray[i,:] =n[1]['wcrd']
            dg = self.og.degree(n[0])
            if( dg == 1 ):
                wc = n[1]['wcrd']
                txt = "(%d,%d,%d)"%(n[0][0],n[0][1],n[0][2])
                
                #self.crds[n[0]] = mlab.text3d(wc[0],wc[1],wc[2],
                #                         "this is a text", color=(0,0,0), scale=2.0)
                s[i] = 1.0
            else:
                s[i] = 0.5
        self.npts = mlab.points3d(self.narray[:,0],self.narray[:,1],self.narray[:,2], s,colormap="gray", scale_factor=4.0)
        self.node_points = self.npts.glyph.glyph_source.glyph_source.output.points.to_array()
        
        # now draw
        
        self.surfaces = {}
        self.lines = {}
        colors = ((1,0,0),(0,1,0),(0,0,1),(1,1,0),(1,0,1),(0,1,1))
        counter = 0
        for e in self.edges:
            try:
                clr = colors[counter%len(colors)]
                counter += 1
                mp = e[2]["mappedPoints"]#np.concatenate((mp,e[2]["mappedPoints"]),axis=0)
                sp = e[2]['d0']
                
                x = mp[::4,0]
                y = mp[::4,1]
                z = mp[::4,2]
                #Visualize the points
                pts = mlab.points3d(x, y, z, scale_mode='none', scale_factor=0.2, opacity=0.0)
                
                # Create and visualize the mesh
                # redirect sys.stderr for this step
                #sys.stderr = self.efile
                mesh = mlab.pipeline.delaunay3d(pts)
                self.surfaces[(e[0],e[1])] = mlab.pipeline.surface(mesh,color=clr,opacity=0.1)
                #sys.stderr = self.stderr
                pts = 0
                if( sp ):
                    self.lines[(e[0],e[1])] = mlab.plot3d(sp[0],sp[1],sp[2],color=clr, tube_radius=1.0)
            except KeyError, error:
                print "KeyError", error
            except IndexError, error:
                print "IndexError", error
        #mlab.view(47, 57, 8.2, (0.1, 0.15, 0.14))
        self.figure.scene.disable_render = False
        print "ready for editing"
        mlab.show()

    def picker_callback(self, pckr):
        # currently this callback gets disconnected when I clear the figure
        # so I am compensating by creating a new figure to draw on with each call
        print "in picker_callback3"
        delta = 2
        surfaceKeys = self.surfaces.keys()
        for sk in surfaceKeys:
            try:
                if( pckr.actor in self.surfaces[sk].actor.actors ):
                    print "we picked a surface"
                    print sk
                    newNode = sk[1]
                    if( self.sg.orderedGraphs[self.key].degree(newNode) == 1 ):
                        if( self.deleteNode == newNode):
                            #mlab.clf(self.editnum)
                            self.sg.pruneSpecifiedDegreeOneNode(self.key,self.deleteNode)
                            self.sg.remapVoxelsToGraph(self.key)
                            self.editnum += 1
                            self.saveModifiedData()
                            self._setGraphData()
                            self._clearGraphDrawables()
                            self.drawGraph()
                            self.deleteNode = None
                            
                        else:
                            self.deleteNode = newNode
                            wcrd = self.sg.orderedGraphs[self.key].node[newNode]['wcrd']
                            outline = mlab.outline(line_width=3)
                            outline.outline_mode = 'cornered'
                            outline.bounds = (wcrd[0]-delta, wcrd[0]+delta, 
                                              wcrd[1]-delta, wcrd[1]+delta, 
                                              wcrd[2]-delta, wcrd[2]+delta)    
                    else:
                        print "This is not a degree 1 node. Degree = %s"%self.sg.orderedGraphs[self.key].degree(newNode)
            except KeyError:
                pass
                # Getting strange key error on redrawing figure after editing.
                # I wonder if this is a qued click from the previous window


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
        parser = OptionParser()
        parser.add_option("-f","--file",dest='fname',
                          help='name or directory for fixedImage')
        parser.add_option("-o","--object_number",dest='objNum',type='int',default='-1')
        parser.add_option('-l','--label',dest='label',default='')

        return parser
    except Exception, error:
        print "failed in getParser", error  
        sys.exit(0)               
        
if __name__ == '__main__':
    parser = getParser()
    (options, args) = parser.parse_args()
    gv = GraphViewer(options.fname, objectnum = options.objNum, keyname=options.label)
    gv.drawGraph()
    
