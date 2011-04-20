#!/usr/bin/env python

import glob
import os
import subprocess

files = glob.glob("PE000??_edited.mha.gz")
for f in files:
    tmp = os.path.splitext(f)
    subprocess.call("getSeanModels.py --img %s -n 10"%tmp[0],shell=True)