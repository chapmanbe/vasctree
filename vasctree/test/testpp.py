#testpp.py
import sys
import pp
sys.path.append("../")
import os

"""The purpose of this code is to run nxvasc.py functions using parallel python"""
def test_nxvascAstar():
    """tests the information gathered using the Astar algorithm"""
    import nxvasc
    import dicom
    import numpy as na
    import fomFuncs
    import costFuncs
    #img=io.readImage("PE00026Filter0_seg.mha", returnITK=False,  imgMode='uchar')
    #mask = na.where(img>0,1,0)
    img=dicom.read_file("data/tree2.dcm")
    array=img.pixel_array
    mask = na.where(array>0, 1, 0)
    vx = nxvasc.nxvasc()
    vx.setMask(mask)
    vx.getMaskMips()
    vx.define3x3_2DEndpointKernels()
    vx.endPointDetection2D()
    vx.viewEndPoints()
    vx.generateRawFigureOfMeritData()
    vx.setFigureOfMeritF(fomFuncs.fomf1)
    vx.setCostFunction(costFuncs.cf1)
    vx.createMaskDictionary()
    vx.fillFigureOfMerit()
    vx.createNXGraph(verbose=True)
    vx.getEndPointPaths() #Uses the astar to find the paths.
    print "trace back paths"
    vx.traceBackPaths4()
    print "prune paths"
    vx.pruneSplitPaths()
    print "plot paths"
    vx.showPaths(vx.paths.values())
    raw_input('continue')
    vx.showPaths(vx.splitPaths,label="Orthogonal MIP Images with Centerlines")
    raw_input('continue')
    vx.plotPaths(vx.splitPaths,label="firstPlot",show=True)
    raw_input('continue')
    
def test_nxvascDijkstra():
    """tests the information gathered using the Dijkstra algorithm"""
    import nxvasc
    import dicom
    import numpy as na
    import fomFuncs
    import costFuncs
    #img=io.readImage("PE00026Filter0_seg.mha", returnITK=False,  imgMode='uchar')
    #mask = na.where(img>0,1,0)
    img=dicom.read_file("data/tree2.dcm")
    array=img.pixel_array
    mask = na.where(array>0, 1, 0)
    vx = nxvasc.nxvasc()
    vx.setMask(mask)
    vx.generateRawFigureOfMeritData()
    vx.setFigureOfMeritF(fomFuncs.fomf1)
    vx.setCostFunction(costFuncs.cf1)
    vx.createMaskDictionary()
    vx.fillFigureOfMerit()
    vx.createNXGraph(verbose=True)
    vx.getDijkstraPaths(verbose=True) #uses the dijkstra algorithm to find paths
    vx.traceBackPaths()
    print "trace back paths"
    vx.pruneSplitPaths()
    print "prune paths"
    vx.showPaths(vx.paths.values())
    raw_input('continue')
    vx.showPaths(vx.splitPaths,label="Orthogonal MIP Images with Centerlines")
    raw_input('continue')
    vx.plotPaths(vx.splitPaths,label="firstPlot",show=True)
    raw_input('continue')
    print "FINISHED"

def main():
    import pp #parallel python
    import time
    ppservers=() #to specify the servers to connect with, we will use the default
    #create the jobserver to automatically detect the number of processors.
    job_server=pp.Server(ppservers=ppservers)
    start_time1=time.time()
    task1=job_server.submit(test_nxvascDijkstra)
    #if the fxn requires something to passed in to it you would put that
    #information in () following the fxn call see ex.
    result1=task1()
    print "Task 1, the Dijkstra test is complete"
    print "Task 1 took", time.time()-start_time1,"s"
    start_time2=time.time()
    task2=job_server.submit(test_nxvascAstar)
    result2=task2()
    print "Task 2, the Astar test is complete"
    print "Task 2 took", time.time()-start_time2,"s"
    job_server.print_stats()

if __name__ == '__main__':
    main()
