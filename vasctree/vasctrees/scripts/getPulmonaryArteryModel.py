#!/usr/bin/env python
from vasctrees.SkeletonGraph import SkeletonGraph
import sys
import scipy.ndimage as ndi
import numpy as np
import argparse
import SimpleITK as sitk
def getParser():
    """Generates command line parser for specifying database and other parameters"""

    parser = argparse.ArgumentParser(description="command line processer for getPulmonaryArteryModel.py")
    parser.add_argument("-s","--skel_img",dest='skel_img',default='',
                      help='file name for skeleton image')
    parser.add_argument("-o","--orig_img",dest='orig_img',
                      help='file name for original image',default=''),
    parser.add_argument("-g","--graph_file",dest="graph_file",default='graph.pckle',
                      help="graph file to write to")
    parser.add_argument("-p","--prune_length",dest="prune_length",type=int,default=5,
                      help="default minimum path length to prune")
    return parser

def main():
    parser = getParser()
    options = parser.parse_args()
    itkimg = sitk.ReadImage(options.skel_img)
    simg = sitk.GetArrayFromImage(itkimg)
    try:
        simg
    except:
        sys.exit("read of skeleton image failed")

    sg = SkeletonGraph(img=simg,
                    spacing=itkimg.GetSpacing(),
                    origin=itkimg.GetOrigin(),
                    orientation=itkimg.GetDirection(),
                    label = options.skel_img)

    print sg.spacing, sg.origin, sg.orientation
    oimg = sitk.GetArrayFromImage(sitk.ReadImage(options.orig_img))

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
    sg.prunePaths(ogkey,options.prune_length)
    sg.deleteDegree2Nodes(ogkey)
    sg.fitEdges(key=ogkey)
    print "Define orthogonal planes"
    sg.defineOrthogonalPlanes(ogkey)
# Now get surface points of original image to map to the centerlines
    dfe = ndi.distance_transform_cdt(oimg)
    points_toMap = np.array(np.nonzero(np.where(dfe==1,1,0))[::-1]).transpose().astype(np.int32)
    print "mapVoxelsToGraph"
    sg.mapVoxelsToGraph(points_toMap,ogkey, verbose=True)
    print "assignMappedPointsToPlanes"
    sg.assignMappedPointsToPlanes(ogkey)
    sg.saveCompressedGraphs(options.graph_file)

if __name__ == '__main__':
    main()
