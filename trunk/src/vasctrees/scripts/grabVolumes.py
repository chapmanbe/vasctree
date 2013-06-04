#!/usr/bin/env python
"""A simple class for grabbing the volume data associated with each
edge in the specified graph


The program is run as a script with three arguments:
skeleton-graph-file object-number graph-key

skeleton-graph-file: a pickle file generated with a SkeletonGraph save
object-number The object number from which the graphs were generated.
(this refers to the sequence of labeled-objects used to generated the graph
and is the integer in the tuple-key used in SkeletonGraph object)

graph-key the string label associated with the graph.

If the graph is modified, a new graph is added to the SkeletonGraph object with
a graph-key equal to the specified graph-key concatenated with '_volume'"""
import cPickle
import numpy as np
import sys
import argparse
from vasctrees.SkeletonGraph import SkeletonGraph
import scipy.ndimage as ndi
import SimpleITK as sitk

class VolumeGrabber(object):
    def __init__(self,fname, objectnum = -1, keyname = '', img='',lvalue=1):
        self.fname = fname
        self.lvalue = lvalue
        f = file(fname)
        self.data = cPickle.load(f)
        f.close()
        self.imgfile = img
        if( objectnum == -1 or keyname == ''):
            self.key = getOrderedGraphKeys(self.data['orderedGraphs'])
        else:
            self.key = (objectnum,keyname)
        self.sg = SkeletonGraph()
        self.sg.orderedGraphs = self.data['orderedGraphs']
        self.sg.roots = self.data['roots']
        if(not self.sg.orderedGraphs[self.key].graph.has_key("root")):
            self.sg.orderedGraphs[self.key].graph["root"] = self.sg.roots[self.key]

        self._setGraphData()    
        # create a new key and copy of graph
        newKey = (self.key[0],"%s_volume"%(self.key[1],))
        self.sg.orderedGraphs[newKey] = self.sg.orderedGraphs[self.key].copy()
        self.key = newKey
   
    def readImage(self):
        sitkimg = sitk.ReadImage(self.imgfile)
        self.simg = sitk.GetArrayFromImage(sitkimg)
        self.dfe = ndi.distance_transform_cdt(self.simg)
        cg = self.sg.orderedGraphs[self.key]
        self.sg.spacing=cg.graph["spacing"]
        self.sg.origin=cg.graph["origin"]
        self.points_toMap = np.array(np.nonzero(np.where(self.simg==self.lvalue,1,0))[::-1]).transpose().astype(np.int32)

    def mapVolumePoints(self,key="volumePoints"):
        #print "in grabVolumes",self.points_toMap
        self.sg.mapVoxelsToGraph(self.points_toMap,self.key,mp_key=key, verbose=True)

    def computeVolumeMeasures(self, key="volumePoints"):
        cg = self.sg.orderedGraphs[self.key]
        edges = cg.edges(data=True)
        for e in edges:
            try:
                mask = np.zeros(cg.graph["imgSize"],np.uint8)
                worldVolume = e[2][key]
# now we need to transform the worldVolume coordinates back to image coordinates
                ivi = ((worldVolume-cg.graph["origin"])/cg.graph["spacing"]).astype(np.int32)
                mask[ivi[:,2],ivi[:,1],ivi[:,0]] = 1
                surface = mask - ndi.binary_erosion(mask)
# now we've got img indicies we can grab the surface based on dfe values
                sinds =  np.nonzero(surface)
                dfeVals = self.dfe[sinds]
                edgeSurface = np.nonzero(dfeVals==1)
                surface_to_volume = float(sinds[0].size)/float(ivi[:,0].size)
                exterior_to_surface = float(edgeSurface[0].size)/float(sinds[0].size)
                e[2]["surface2volume"] = surface_to_volume
                e[2]["exterior2surface"] = exterior_to_surface
            except ValueError:
                e[2]['surface2volume'] = None
                e[2]['exterior2surface'] = None

    def saveModifiedData(self):
        print "saving modified data"
        self.data['orderedGraphs'] = self.sg.orderedGraphs
        f = file(self.fname,"wb")
        cPickle.dump(self.data,f)
    def _setGraphData(self):
        self.og = self.sg.orderedGraphs[self.key]
        self.edges = self.og.edges(data=True)
        self.nodes = self.og.nodes(data=True)
        
        

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
        parser = argparse.ArgumentParser(description="command line processor for grabVolumes")
        parser.add_argument("-f","--file",dest='fname',
                          help='name or directory for fixedImage')
        parser.add_argument("-o","--object_number",dest='objNum',type='int',default='-1')
        parser.add_argument("-v","--value",dest="lvalue",type='int',default='1')
        parser.add_argument("-i","--img",dest="img",default="",help="name or directory of segmented image")
        parser.add_argument('-l','--label',dest='label',default='')

        return parser
    except Exception, error:
        print "failed in getParser", error  
        sys.exit(0)               
        
if __name__ == '__main__':
    parser = getParser()
    (options, args) = parser.parse_args()
    gv = VolumeGrabber(options.fname, objectnum = options.objNum, 
                       keyname=options.label,img=options.img,
                       lvalue=options.lvalue)
    gv.readImage()
    gv.mapVolumePoints()
    gv.computeVolumeMeasures()
    gv.saveModifiedData()
    
