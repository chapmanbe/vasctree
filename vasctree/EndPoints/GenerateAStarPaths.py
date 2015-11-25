import sys
sys.path.append("../../vasctrees")
import os
import nxvasc
import imageTools.ITKUtils.io as io
import numpy as na
import fomFuncs
import costFuncs
import pickle

def A_Star():
    img=io.readImage("PE00025Filter0_seg.mha", returnITK=False, imgMode='uchar')
    mask=na.where(img>0,1,0)
    instance=nxvasc.nxvasc()
    instance.setmask(mask)
    indexes=open("Indexes.pckle",'rb')
    inds=pickle.load(indexes)
    graph=open("PE00025NXgraph.pckle",'rb')
    G=pickle.load(graph)
    instance.generateRawFigureOfMerit()
    instance.setFigureOfMeritF(fomFuncs.fom1)
    instance.setCostFunction(costFuncs.cf1)
    instance.GenerateAstarPaths(G, inds)
    path=open("PE00025A_StarPaths.pckle", 'wb')
    pickle.dump(self.paths,  path)
if __name__ == '__main__':
    A_star() 
    

