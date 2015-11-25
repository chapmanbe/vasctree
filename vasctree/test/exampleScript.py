import VascTree
import sys
import os
from compare_bifurcation_locs import *
import time
# processed using seedpoints determined from automated detection algorithm
# in IDL
def main():
    try:
        b = VascTree.VascTree(fileroot="data/")
        b.setMaskfile(".zbs_mask")
        b.min_path_length = 20
        b.vsuffix = "_VascTree_utah"
#b.min_path_length = 3
#b.min_path_length = 0
#b.epn = b.get_new_neighbors124
        fargs.write(repr(b.epn)+"\n")

	    fargs.write(repr(b.cf)+"\n")
            print "using alpha ", b.alpha, ", beta ",b.beta,", gamma ",b.gamma," and noise ",b.noise
            b.fill_values(mode=0)
            b.process()
	elif( compute_cf == 'load' ):
	    b.fill_values(mode=0)

	    b.load_data(rpaths=0,fpaths=0)
	    b.load_dijkstra_file()
	    b.generate_dijkstra_cost_img()
	    b.show = 1
        b.draw_paths()

	    b.save_path_img(suffix="filterfom_dijkstra_paths.png")
	    raw_input("continue")
	    return
	else:
	    if( len(sys.argv) > 3 ):
		mode = int(sys.argv[3])
	    if( len(sys.argv) > 4 ):
		b.carve_path = int(sys.argv[4])
        if( compute_cf == 'yes' ):
	    b.processPaths(read_data=0,mode=2, gsanalysis = 'no')
	else:
	    print "processing paths"
            b.processPaths(mode=mode, gsanalysis = 'no', dijkstra = 'yes')
    except Exception, error:
	print "failed in run_VascTree.main() ", error
def test5():
    try:
	sys.argv = ['test5','load']
	main()
    except Exception, error:
	print "failed in test5()",error
	sys.exit()

def test4():
    try:
	sys.argv = ['test4','0','yes','0.5','0.1','1','0','bcf4']
	main()
    except Exception, error:
	print "failed in test4()",error
	sys.exit()
def test3():
    try:
	sys.argv = ['test','0','no','2']
	main()
    except Exception, error:
	print "failed in test()",error
	sys.exit()

def test2():
    try:
	sys.argv = ['test','no','2']
	main()
    except Exception, error:
	print "failed in test()",error
	sys.exit()

def test():
    try:
	sys.argv = ['test','yes','5']
	main()
    except Exception, error:
	print "failed in test()",error
	sys.exit()

if __name__ == '__main__':
   #main()
    test4()
