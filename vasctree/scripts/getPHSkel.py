#!/usr/bin/env python
from vasctrees.SkeletonGraph import SkeletonGraph
#import imageTools.ITKUtils.io as io
import sys
#img = io.readImage(sys.argv[1],returnITK=True,imgMode='uchar')
import dicom
def main():
    dcm = dicom.read_file(sys.argv[1])
    img=dcm.pixel_array
    sg = SkeletonGraph(img)
    arg2 = dicom.read_file(sys.argv[2])
    img2 = arg2.pixel_array
    sg.setOriginalImage(img2)
#sg.setOriginalImage(fname=sys.argv[2])
    sg.getGraphsFromSkeleton(verbose=False)
    sg.setLargestGraphToCurrentGraph()
    sg.graphs.keys()
    sg.findEndpointsBifurcations()
    root = sg.selectSeedFromDFE()
#sg.viewGraph()
#raw_input('continue')
    sg.setRoot(root,key="test")
    sg.traceEndpoints(key='test')
    ogkey = sg.getLargestOrderedGraphKey()
    sg.deleteDegree2Nodes(ogkey)
    sg.prunePaths(ogkey)
    sg.deleteDegree2Nodes(ogkey)
    sg.fitEdges(key=ogkey)
    og = sg.orderedGraphs[ogkey]
    sg.viewGraph(og)
    sg.saveGraphs(sys.argv[3])

if __name__ == '__main__':
    main()
