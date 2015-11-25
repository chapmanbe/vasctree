#!/usr/bin/env python
import sys
import os
import subprocess
from optparse import OptionParser
import glob
import re

def getParser():
    try:
        
        usage = """This program reads in a skeleton image stored in a standard 3D image format (e.g. meta image). """+\
                """The program will first check to see if the image is compressed in a gnuzip format and will uncompress it if necessary. """+\
                """The program also needs an origin file that will be used to set the origins for the graphs. """+\
                """Currently the origins need to be stored in a Pickle file and be in the CritPoint format. """+\
                """For each specified origin, the program will order the created graph based on that origin. """+\
                """Thus the graphs are duplicated for each origin."""
        parser = OptionParser(usage=usage)
        parser.add_option("-i", "--img", dest="filename", help="binary image to read and threshold", default=".dcm")
        parser.add_option("-o", "--origins", dest="originsFile", help="file containing the arterial and venous origins for this subject",
                          default="")
        parser.add_option("-n", "--numIter", dest="iterations",type="int",default=10)

        return parser
    except Exception,  error:
        print "failed to generate parser",  error
        


def main():
    files = glob.glob("PE?????_edited_fill_skel.mha.gz")
    for file in files:
        print file
        #su = subprocess.call("gunzip %s"%file,shell=True)
        tmp = os.path.splitext(file)
        r1 = re.compile(r"""PE(\d{5,5})_edited""")
        caseNum = "%04d.mps.pckle"%(int(r1.findall(tmp[0])[0]))
        print tmp[0],caseNum
        sg = subprocess.call("getSeanGraphs.py --img %s --origins %s"%(tmp[0],os.path.join("..","seanOrigins",caseNum)),shell=True)
        #sc = subprocess.call("gzip %s"%tmp[0],shell=True)

if __name__ == '__main__':
    main()
