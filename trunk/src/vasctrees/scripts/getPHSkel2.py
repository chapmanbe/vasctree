#!/usr/bin/env python
from vasctrees.SkeletonGraph import SkeletonGraph
import imageTools.ITKUtils.io as io
import sys
import scipy.ndimage as ndi
import numpy as np

simg,descr = io.readImage( sys.argv[1],
                          returnITK=False,
                         imgMode='uchar',
                         returnDescriptors = True)
try:
    simg
except:
    sys.exit("read of skeleton image failed")

sg = SkeletonGraph(img=simg,
                   spacing=descr['scale'],
                   origin=descr['origin'],
                   orientation=descr['orientation'],
		   label = sys.argv[1])

print descr
print sg.spacing, sg.origin, sg.orientation

oimg = io.readImage( sys.argv[2],returnITK=False,imgMode='uchar')
try:
    oimg
except:
    sys.exit("read of mask image failed")
sg.setOriginalImage(oimg)
sg.getGraphsFromSkeleton(verbose=False)
sg.setLargestGraphToCurrentGraph()
sg.graphs.keys()
sg.findEndpointsBifurcations()
root = sg.selectSeedFromDFE()
#sg.viewGraph()
#raw_input('continue')
sg.setRoot(root,key="mp_graphs")
sg.traceEndpoints(key='mp_graphs')
ogkey = sg.getLargestOrderedGraphKey()
sg.deleteDegree2Nodes(ogkey)
sg.prunePaths(ogkey)
sg.deleteDegree2Nodes(ogkey)
sg.fitEdges(key=ogkey)
print "Define orthogonal planes"
sg.defineOrthogonalPlanes(ogkey)
# Now get surface points of original image to map to the centerlines
dfe = ndi.distance_transform_cdt(oimg)
points_toMap = np.array(np.nonzero(np.where(dfe==1,1,0))[::-1]).transpose().astype(np.int32)
print "mapVoxelsToGraph"
sg.mapVoxelsToGraph(points_toMap,ogkey)
print "assignMappedPointsToPlanes"
sg.assignMappedPointsToPlanes(ogkey)
sg.saveCompressedGraphs(sys.argv[3])
