#!/usr/bin/env python
"""This is used with the viewer for manually labeling endpoints of the vessels. 
The output is called f)MipEndpoints.pckle which contains the coordinate locations for each point."""
import os
import subprocess

# get the 
dirName = os.path.basename(os.getcwd())
cmd = """itkView --img %sFilter0_seg.mha --labelFile /HD1/Defs/miplabels.txt --colorFile /HD1/Defs/mipcolors.txt --pointsFile f0MipEndpoints.pckle"""%dirName 
print(dirName)
print(cmd)
rslt = subprocess.call(cmd,shell=True)
