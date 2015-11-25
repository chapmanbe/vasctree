#!/usr/bin/env python
from vasctrees.SkeletonGraph import SkeletonGraph
import vasctrees.SkeletonGraph as skgs
import sys
import scipy.ndimage as ndi
import numpy as np
import SimpleITK as sitk

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

    try:
        simg
    except:
        sys.exit("read of skeleton image failed")

    sg = SkeletonGraph(img=simg,
                    spacing=descr['scale'],
                    origin=descr['origin'],
                    orientation=descr['orientation'],
                    label = sys.argv[1])

##print descr
#print sg.spacing, sg.origin, sg.orientation

    oimg,tmp = readImage( sys.argv[2])
    try:
        oimg
    except:
        sys.exit("read of mask image failed")
    sg.setOriginalImage(oimg)
    sg.getGraphsFromSkeleton(verbose=False)
    sg.setLargestGraphToCurrentGraph()
    list(sg.graphs.keys())
    sg.findEndpointsBifurcations()
    endp = [n for n in sg.cg.nodes() if sg.cg.degree(n)==1]
    endpa = np.array(endp)
    medianx = np.median(endpa[:,0])
    endp.sort(key=lambda n: abs(n[0]-medianx))
    root = endp[0]
#sg.viewGraph()
    sg.setRoot(root,key="og_medianx")
    sg.traceEndpoints(key='og_medianx')
    ogkey = sg.getLargestOrderedGraphKey()
    sg.deleteDegree2Nodes(ogkey)
    sg.prunePaths(ogkey)
    sg.deleteDegree2Nodes(ogkey)
    sg.fitEdges(key=ogkey)
#print "Define orthogonal planes"
    sg.defineOrthogonalPlanes(ogkey)
# Now get surface points of original image to map to the centerlines
    dfe = ndi.distance_transform_cdt(oimg)
    points_toMap = np.array(np.nonzero(np.where(dfe==1,1,0))[::-1]).transpose().astype(np.int32)
#print "mapVoxelsToGraph"
    sg.mapVoxelsToGraph(points_toMap,ogkey)
#print "assignMappedPointsToPlanes"
    sg.assignMappedPointsToPlanes(ogkey)
    sg.saveCompressedGraphs(sys.argv[3])

if __name__ == '__main__':
    main()
