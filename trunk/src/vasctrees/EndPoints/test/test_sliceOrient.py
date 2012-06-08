import sys
sys.path.insert(0,"../")
import numpy as na

import sliceOrientation as so

class TestSliceOrient(object):
    def setUp(self):
        self.m1 = na.zeros((3,3,3),na.uint8)
        self.m1[0,0:2,0:2] = 1
        self.m1[1,0:2,1] = 1
        
        #self.m2 = na.zeros((3,3,3),na.uint8)
        #self.m2[0:2,0,0:2] = 1
        #self.m2[0:2,1,1] = 1
        self.m2 = na.transpose(self.m1,(1,0,2))
        self.m2 = self.m2[:,::-1,:]
        #
        #
        #self.m3 = na.zeros((3,3,3),na.uint8)
        #self.m3[0:2,0:2,0] = 1
        #self.m3[0:2,1,1] = 1
        self.m3 = na.transpose(self.m1,(2,1,0))
        

    def tearDown(self):
        self.m1 = 0
        self.m2 = 0
        self.m3 = 0
    def testYtoZ(self):
        a = self.m2.copy()
        aso = so.OrientMask(a)
        aso.orient()
        print "aso.mask"
        print aso.mask
        print "m1"
        print self.m1
        print "m2"
        print self.m2
        assert not (self.m1 - aso.mask).any()
    def testXtoZ(self):
        a = self.m3.copy()
        aso = so.OrientMask(a)
        aso.orient()
        print "aso.mask"
        print aso.mask
        print "m1"
        print self.m1
        print "m3"
        print self.m3
        assert not (self.m1 - aso.mask).any()
        
def main():
    t = TestSliceOrient()
    t.setUp()
    t.testYtoZ()
    t.testXtoZ()
if __name__ == '__main__':
    main()
    