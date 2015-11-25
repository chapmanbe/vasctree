#!/usr/bin/env python
"""
This is a rewrite of the smoothSeg.py script with SimpleITK routines
replacing the WrapITK routines
"""
import SimpleITK as sitk
import sys
import os

from optparse import OptionParser

def getParser():
    """create an OptionParser instance and create parsing rules"""
    try:
        parser = OptionParser()
        parser.add_option("-k", "--kernel", dest='kernel',nargs=3,
                          default=(1,1,1),type='int')
        parser.add_option("-f", "--file", dest='fname',default='')
        parser.add_option("-m", "--median",action='store_true', dest='median',default=False)
        parser.add_option("-c", "--close",action='store_true', dest='close',default=False)
        return parser
    except Exception as  error:
        print("failed to generate parser",  error)

def dilateMask(fname, median, closing, kernel):
    """dilate the binary mask passed in with the positional argument img.
    Prior to dilation an sitk.MedianImageFilter is used with a (1,1,1)
    kerenl
    
    Dilation is applied using the sitk.BinaryDilateImageFilter"""
    # If user didn't provide a kernel size, use the default value
    fmod = ""
    # get image range
    
    img = sitk.ReadImage(fname)
    if( median ):
        print("running median")
        fmod += "_median_True"
        median = sitk.MedianImageFilter()
        median.SetRadius([1,1,1])
        img = median.Execute(img)
    else:
        fmod += "_median_False"
    if( closing ):
        print("running closing")
        fmod += "_closing_True_kernel_%d_%d_%d"%(kernel[0],kernel[1],kernel[2])
        closing = sitk.BinaryMorphologicalClosingImageFilter()
        closing.SetForegroundValue(1)
        closing.SetKernelRadius(kernel)
        img = closing.Execute(img)
    else:
        fmod += "_closing_False"
    # this is a really, really slow step
    tmp = fname.split(".nii.gz")
    sitk.WriteImage(img, tmp[0]+fmod+".nii.gz")
def main():
        
    parser = getParser()
    (options, args) = parser.parse_args()
    print(options)
    dilateMask(options.fname, options.median, options.close,options.kernel)

        
if __name__=='__main__':
    main()
        
        
        
