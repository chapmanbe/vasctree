"""
A series of tests to validate the peformance of the nxvasc class as well as
the associated classes RelatedPoints and Path
"""
"""Modifying the testing structure to include a class setup and teardown"""
import sys
sys.path.insert(0, "../")
import os
import numpy as na
import time
import copy
import nxvasc
import dicom
import fomFuncs
import costFuncs
import imageTools.ITKUtils.io as io

class testClass:
    def setUp(self):
        """setUp is called before each test is run, tearDown is called after"""
        self.img=dicom.read_file("data/tree2.dcm")
        self.array=self.img.pixel_array
        self.mask = na.where(self.array>0, 1, 0)
        self.vx = nxvasc.nxvasc()
        self.vx.setMask(self.mask)
        self.vx.getMaskMips()
        self.vx.define3x3_2DEndpointKernels()
        self.vx.endPointDetection2D()
        self.vx.generateRawFigureOfMeritData()
        self.vx.setFigureOfMeritF(fomFuncs.fomf1)
        self.vx.setCostFunction(costFuncs.cf1)
        self.vx.createMaskDictionary()
        self.vx.fillFigureOfMerit()
        self.vx.createNXGraph(verbose=True)
    def tearDown(self):
        pass
        
    def test_nxvasc1(self):
        """Uses an exhaustive search for determining the bifurcation points"""
        self.vx.getDijkstraPaths(verbose=True)
        temp1 = copy.deepcopy(self.vx.paths)
        t4_start = time.time()
        self.vx.traceBackPaths4()
        t4_stop = time.time()
        self.vx.paths = copy.deepcopy(temp1)
        t2_start = time.time()
        self.vx.traceBackPaths2()
        t2_stop = time.time()
        self.vx.paths = copy.deepcopy(temp1)
        t1_start = time.time()
        self.vx.traceBackPaths1()
        t1_stop = time.time()
        print("time for algorithm4:",t4_stop-t4_start)
        print("time for algorithm2:",t2_stop-t2_start)
        print("time for algorithm1:",t1_stop-t1_start)    

    def test_SegGraph(self):
        self.vx.getEndPointPaths()
        print("trace back paths")
        self.vx.traceBackPaths5()
        print("plot paths")
        self.vx.showPaths(self.vx.getSGPaths(),label="Orthogonal MIP Images with Centerlines-SG")
        input('continue')

    def test_mipEndPoints(self):
        self.vx.getEndPointPaths()
        print("trace back paths")
        self.vx.traceBackPaths4()
        print("prune paths")
        self.vx.pruneSplitPaths()
        print("plot paths")
        self.vx.showPaths(list(self.vx.paths.values()))
        input('continue')
        self.vx.showPaths(self.vx.splitPaths,label="Orthogonal MIP Images with Centerlines")
        input('continue')
        self.vx.plotPaths(self.vx.splitPaths,label="firstPlot",show=True)
        input('continue')
    
    def test_nxvasc(self):
        """Uses sets for determining bifurcation points"""
        self.vx.getDijkstraPaths(verbose=True)
        self.vx.traceBackPaths()
        self.vx.pruneSplitPaths()
        self.vx.plotPaths(label="firstPlot",show=True)
        print("FINISHED")

    def createPhantom1(self):
        self.mask = na.zeros((16,32,32),na.uint16)
        self.mask[8:11,14:18,:] = 1
        self.mask[9,:,14] = 1
        return self.mask
        
    def createPhantom2(self):
        self.mask = na.zeros((16,32,32),na.uint16)
        self.mask[6:13,12:20,:] = 1
        self.mask[9,:,14] = 1
        return self.mask
        
    def createPhantom3(self):
        self.mask  = na.zeros((16,32,32),na.uint16)
        self.mask[9,16,1:-2] = 1
        for i in range(8,32,4):
           self.mask[9,2:30,i] = 1
        return self.mask

#if __name__ == '__main__':

