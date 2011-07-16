#!/usr/bin/env python
import glob
import os
import sys
import subprocess
import itk
from optparse import OptionParser


def fillHoles(fname):
    print "filling in",fname
    reader = itk.ImageFileReader.IUC3.New(FileName=fname)
    filler = itk.VotingBinaryIterativeHoleFillingImageFilter.IUC3.New()
    filler.SetInput(reader.GetOutput())
    
    tmp2 = os.path.splitext(fname)
    outFill = tmp2[0]+"_fill.mha"
    writer = itk.ImageFileWriter.IUC3.New(FileName=outFill)
    
    writer.SetInput(filler.GetOutput())
    writer.Update()
    print "saved filled file",outFill
    return outFill
def getParser():
    try:
        parser = OptionParser()
        parser.add_option("-i", "--imgs", dest="filename", help="binary image to read and threshold", default="PE?????_edited.mha")
        parser.add_option("-n", "--numIter", dest="iterations",type="int",default=10)

        return parser
    except Exception,  error:
        print "failed to generate parser",  error
        


def main():
    try:
        parser = getParser()
        (options, args) = parser.parse_args()
        files = glob.glob(options.filename+".gz")
        for file in files:
            print "Current file",file
            ofile = os.path.splitext(file)[0]
            print "processing original file",ofile
            subprocess.call("gunzip %s"%file,shell=True)
            ffile = fillHoles(ofile)
            tmp2 = os.path.splitext(ffile)
            outSkel = tmp2[0]+"_skel.mha"
    
            subprocess.call("BinaryThinning3D %s %s"%(ffile,outSkel),shell=True)
            print "compressing files",ofile,outSkel
            subprocess.call("gzip %s %s %s"%(ofile,outSkel,ffile),shell=True)

    except Exception, error:
        print "failed in getSkeletons due to error:",error
        print options.filename, outSkel

if __name__ == '__main__':
    main()
