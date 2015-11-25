import sys
sys.path.insert(0,"../")

import VascMask
import VascGraph
import numpy as na
import costFuncs
import time
def main():
    mask = na.zeros((32,128,128))
    mask[13:18,10:120,62:68] =  1
    mask[13:18,62:68,10:120] =  1
    vm = VascMask.VascMask()
    vm.setMask(mask)
    vm.setNeighborhoodSize()
    vm.getFOM()
    vm.setCostFunction(costFuncs.cf1)
    startTime = time.time()
    vm.createNXGraph()
    endTime = time.time()
    print("Elapsed time",endTime-startTime)
    print("number of edges",vm.G.number_of_edges())
    vg = VascGraph.VascGraph(vm.G)
    vg.getAPaths(vm.findSeed(), vm.getSurfacePoints())
    #vm.G = None
    #startTime = time.time()
    #vm.createNXGraphPP()
    #endTime = time.time()
    #print "Elapsed time",endTime-startTime
    #print "number of edges",len(vm.edges)
    
if __name__ == '__main__':
    main()
    