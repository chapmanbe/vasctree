import os
import sys
#sys.path.append('../../vasctrees')
#import vasctrees.nxvasc as nxvasc
import pickle
import numpy as na
import scipy.ndimage as ndi
import math
#import imageTools.ITKUtils.io as io

class OrientMask(object):
    """A class for organizing the functions necessary to ensure that 
    all the endpoints are rotated into the same direction along the Z-axis"""
    def __init__(self, mask):
        self.mask = mask
        self.debug = True
        
    def facesZ(self):
        """facesZ, Y, X are the functions we use to determine the direction 
        of rotation based on the resulting direction and magnitude of the vectors for each axis"""
        sumBeginning=self.mask[0, :, :].sum()
        sumEnd=self.mask[-1, :, :].sum()
        return int(sumEnd-sumBeginning)
    def facesY(self):
        sumBeginning = self.mask[:, 0, :].sum()
        sumEnd = self.mask[:, -1, :].sum()
        return int(sumEnd-sumBeginning)
    def facesX(self):
        sumBeginning = self.mask[:, :, 0].sum()
        sumEnd = self.mask[:, :, -1].sum()
        return int(sumEnd-sumBeginning)
    
    def yToz(self):
        """we want all to be in the z direction. If the axis with the largest magnitude is y then we must rotate back to the z direction"""
        #if( self.debug ):
            #print "yToz"
        self.mask = na.transpose(self.mask, (1,0,2))
    def xToz(self):
        """we want all to be in the z direction. If the axis with the largest magnitude is x then we must rotate back to the z direction"""
        #if( self.debug ):
            #print "xToz"
        self.mask = na.transpose(self.mask, (2,1,0))
        
    def reverseX(self):
        """This function flips the whole array from left to right"""
        #Ex. [0,0,1] = [1,0,0]
        #if( self.debug ):
            #print "reverseX"
        self.mask = self.mask[:,:,::-1]
    def reverseY(self):
        """This function flips each slice from top to bottom"""
        #Ex. [0,1,0]   [0,0,0]
        #    [0,0,0] = [0,1,0]
        #if( self.debug ):
            #print "reverseY"
        self.mask = self.mask[:,::-1,:]
    def reverseZ(self):
        """This function all slices together end over end"""
        #Ex. slice1= [0,1,0]   [0,0,0]
        #    slice2= [1,1,1] = [1,1,1]
        #    slice3= [0,0,0]   [0,1,0]
        #if( self.debug ):
            #print "reverseZ"
        self.mask = self.mask[::-1,:,:]
    def orient(self):
        mx = self.facesX()
        my = self.facesY()
        mz = self.facesZ()
        #print type(mx), type(my), type(mz)
        #print "mx %d; my %d; mz %d"%(mx, my, mz)
        #print "amx %d; amy %d; amz %d"%(abs(mx), abs(my), abs(mz))
        
        if( abs(mx) > abs(my) and abs(mx) > abs(mz) ):
            #print "Processing x to z"
            if( mx > 0 ):
                self.reverseX()
            self.xToz()
        elif( abs(my) > abs(mx) and abs(my) > abs(mz) ):
            #print "processing y to z"
            if( my > 0 ):
                self.reverseY()
            self.yToz()
        else:
            #print "processing z"
            if( mz > 0 ):
                self.reverseZ()

    


