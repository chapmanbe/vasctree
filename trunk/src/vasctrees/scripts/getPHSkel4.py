#!/usr/bin/env python
from vasctrees.SkeletonGraph import SkeletonGraph
import vasctrees.SkeletonGraph as skgs
import sys
import scipy.ndimage as ndi
import numpy as np
import SimpleITK as sitk
import numpy as np

import multiprocessing as mp

def rootRMS(graph):
    endp = [(n[0],n[1]['wcrd']) for n in graph.nodes(data=True) if graph.degree(n[0]) == 1]
    endpa = np.array([n[0] for n in endp])
    maxk = np.max(endpa[:,2])
    endp.sort(key=lambda n: np.sqrt((n[0][0]-256)**2+(n[0][1]-0)**2+(n[0][2]-maxk)**2))
    newRoot = endp[0][0]
    return newRoot

def readImage(fname):
    img = sitk.ReadImage(fname)
    aimg = sitk.GetArrayFromImage(img)
    descriptors = {}
    descriptors["scale"] = img.GetSpacing()
    descriptors["origin"] = img.GetOrigin()
    descriptors["orientation"] = img.GetDirection()
    return aimg, descriptors

def main():
    simg,descr = readImage( sys.argv[1] )

    pool = mp.Pool(mp.cpu_count())

    try:
        simg
    except:
        sys.exit("read of skeleton image failed")

    sg = SkeletonGraph(img=simg,
                    spacing=descr['scale'],
                    origin=descr['origin'],
                    orientation=descr['orientation'],
                    label = sys.argv[1],
                    pool = pool)

##print descr
#print sg.spacing, sg.origin, sg.orientation

    oimg,tmp = readImage( sys.argv[2])
    try:
        oimg
    except:
        sys.exit("read of mask image failed")
    sg.setOriginalImage(oimg)
    sg.getGraphsFromSkeleton(verbose=True)
    sg.setLargestGraphToCurrentGraph()
    sg.graphs.keys()
    sg.findEndpointsBifurcations()
    print "set root"
    root = rootRMS(sg.cg)
#sg.viewGraph()
    sg.setRoot(root,key="og_rms")
    print "trace endpoints"
    sg.traceEndpoints(key='og_rms')
    ogkey = sg.getLargestOrderedGraphKey()
    print "prune tree"
    sg.deleteDegree2Nodes(ogkey)
    sg.prunePaths(ogkey)
    sg.deleteDegree2Nodes(ogkey)
    print "fit edges"
    sg.fitEdges(key=ogkey)
    print "Define orthogonal planes"
    sg.defineOrthogonalPlanes(ogkey)
    print "Now get surface points of original image to map to the centerlines"
    dfe = ndi.distance_transform_cdt(oimg)
    points_toMap = np.array(np.nonzero(np.where(dfe==1,1,0))[::-1]).transpose().astype(np.int32)
    print "mapVoxelsToGraph"
    sg.mapVoxelsToGraph(points_toMap,ogkey)
    print "assignMappedPointsToPlanes"
    sg.assignMappedPointsToPlanes(ogkey)
    sg.saveCompressedGraphs(sys.argv[3])

if __name__ == '__main__':
    main()
