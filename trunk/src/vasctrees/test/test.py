"""
A series of tests to validate the peformance of the nxvasc class as well as
the associated classes RelatedPoints and Path
"""
#import nxvasc
import sys
import os
import numpy as na
import time
import copy

#def test_itk():
    #import itk
    #assert itk
def test_dicom():
    import dicom
    assert dicom
def test_scipy():
    import scipy
    assert scipy
import sys
sys.path.insert(0,"../")
def test_numpy():
    import numpy
    assert numpy

#def test_io():
    #import imageTools.ITKUtils.io as io
    #assert io

def test_importfomFuncs():
    import fomFuncs
    assert fomFuncs

def test_endPointsFromCritPoints():
    assert False

def test_nxvasc1():
    """Uses an exhaustive search for determining the bifurcation points"""
    import nxvasc
    import fomFuncs
    import costFuncs
    import dicom   
    img=dicom.read_file("data/tree2.dcm")
    array=img.pixel_array
    mask = na.where(array>0, 1, 0)
    #mask = createPhantom2()
    vx = nxvasc.nxvasc() #calls the class nxvasc and fxn 3x3matrix
    vx.setOutputFile("testnx1.out") #Sets the objects mask to image located in the maskfile
    vx.setMask(mask) 
    vx.generateRawFigureOfMeritData()
    vx.setFigureOfMeritF(fomFuncs.fomf1)
    vx.setCostFunction(costFuncs.cf1)
    vx.createMaskDictionary()
    vx.fillFigureOfMerit()
    vx.createNXGraph(verbose=True)
    vx.getDijkstraPaths(verbose=True)
    temp1 = copy.deepcopy(vx.paths)
    t4_start = time.time()
    vx.traceBackPaths4()
    t4_stop = time.time()
    vx.paths = copy.deepcopy(temp1)
    t2_start = time.time()
    vx.traceBackPaths2()
    t2_stop = time.time()
    vx.paths = copy.deepcopy(temp1)
    t1_start = time.time()
    vx.traceBackPaths1()
    t1_stop = time.time()
    print "time for algorithm4:",t4_stop-t4_start
    print "time for algorithm2:",t2_stop-t2_start
    print "time for algorithm1:",t1_stop-t1_start
def test_critEnds():
    import nxvasc
    import dicom
    import fomFuncs
    import costFuncs
    import imageTools.ITKUtils.io as io
    #img=dicom.read_file("data/tree2.dcm")
    #array=img.pixel_array
    #mask = na.where(array>0, 1, 0)
    img = io.readImage("data/p16Mask.mha",returnITK=False,imgMode="uchar")
    mask = na.where(img>0,1,0)
    #mask = createPhantom3()
    vx = nxvasc.nxvasc()
    vx.setOutputFile("testnx.out")
    vx.setMask(mask)
    vx.getMaskMips()
    vx.endPointsFromCritPoints("data/ends.pckle")
    vx.generateRawFigureOfMeritData()
    vx.setFigureOfMeritF(fomFuncs.fomf1)
    vx.setCostFunction(costFuncs.cf1)
    vx.createMaskDictionary()
    vx.fillFigureOfMerit()
    vx.createNXGraph(verbose=True)
    vx.getEndPointPaths()
    print "trace back paths"
    vx.traceBackPaths5()
    print "plot paths"
    vx.showPaths(vx.getSGPaths(),label="Orthogonal MIP Images with Centerlines-SG")
    raw_input('continue')
def test_SegGraph():
    import nxvasc
    import dicom
    import fomFuncs
    import costFuncs
    import imageTools.ITKUtils.io as io
    #img=dicom.read_file("data/tree2.dcm")
    #array=img.pixel_array
    #mask = na.where(array>0, 1, 0)
    img = io.readImage("data/p16Mask.mha",returnITK=False,imgMode="uchar")
    mask = na.where(img>0,1,0)
    #mask = createPhantom3()
    vx = nxvasc.nxvasc()
    vx.setOutputFile("testnx.out")
    vx.setMask(mask)
    vx.getMaskMips()
    vx.define3x3_2DEndpointKernels()
    vx.endPointDetection2D()
    vx.generateRawFigureOfMeritData()
    vx.setFigureOfMeritF(fomFuncs.fomf1)
    vx.setCostFunction(costFuncs.cf1)
    vx.createMaskDictionary()
    vx.fillFigureOfMerit()
    vx.createNXGraph(verbose=True)
    vx.getEndPointPaths()
    print "trace back paths"
    vx.traceBackPaths5()
    print "plot paths"
    vx.showPaths(vx.getSGPaths(),label="Orthogonal MIP Images with Centerlines-SG")
    raw_input('continue')

def test_mipEndPoints():
    import nxvasc
    import dicom
    import fomFuncs
    import costFuncs
    img=dicom.read_file("data/tree2.dcm")
    array=img.pixel_array
    mask = na.where(array>0, 1, 0)
    #mask = createPhantom3()
    vx = nxvasc.nxvasc()
    vx.setOutputFile("testnx.out")
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
    vx.getEndPointPaths()
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
def test_nxvasc():
    """Uses sets for determining biforcation points"""
    import nxvasc
    import fomFuncs
    import costFuncs
    import dicom
    vx = nxvasc.nxvasc()
    vx.setOutputFile("testnx.out")
    vx.setMask(mask)
    vx.generateRawFigureOfMeritData()
    vx.setFigureOfMeritF(fomFuncs.fomf1)
    vx.setCostFunction(costFuncs.cf1)
    vx.createMaskDictionary()
    vx.fillFigureOfMerit()
    vx.createNXGraph(verbose=True)
    vx.getDijkstraPaths(verbose=True)
    vx.traceBackPaths()
    vx.pruneSplitPaths()
    vx.plotPaths(label="firstPlot",show=True)
    print "FINISHED"
    #Tree = v.traceBackGraph()
    #assert vx.splitPaths
def test_vasc():
    import vasc
    import fomFuncs
    import costFuncs
    import dicom
    #print vasc.__file__
    img=dicom.read_file("data/tree2.dcm")
    array=img.pixel_array
    mask = na.where(array>0, 1, 0)
    v = vasc.vasctree()
    v.setOutputFile("test.out")
    v.setMask(mask)
    v.generateRawFigureOfMeritData()
    v.setFigureOfMeritF(fomFuncs.fomf1)
    v.setCostFunction(costFuncs.cf1)
    v.createMaskDictionary()
    v.fillFigureOfMerit()
    v.createGraph(verbose=True)
    v.getDijkstraPaths(verbose=True)
    v.traceBackPaths()
    v.setMinPathLength(8)
    v.pruneSplitPaths()
    v.plotPaths(label="firstPlot",show=True)
    assert v.maxPath

def createPhantom1():
    mask = na.zeros((16,32,32),na.uint16)
    mask[8:11,14:18,:] = 1
    mask[9,:,14] = 1
    return mask
def createPhantom2():
    mask = na.zeros((16,32,32),na.uint16)
    mask[6:13,12:20,:] = 1
    mask[9,:,14] = 1
    return mask
def createPhantom3():
    mask  = na.zeros((16,32,32),na.uint16)
    mask[9,16,1:-2] = 1
    for i in range(8,32,4):
        mask[9,2:30,i] = 1

    return mask

if __name__ == '__main__':
    import sys
    test_critEnds()
