import numpy as na
def fomf1(fom):
    try:
        return fom.max()-fom
    except Exception, error:
        print "failed in fomf1() ", error
        sys.exit()  
def fomf2(fom):
    try:
        return 1.0/fom
    except Exception, error:
        print "failed in fomf2() ", error
        sys.exit()
        
def fomf3(fom):
    try:
        computed_new_mdfe = 0
        if( self.read_mdfe_values() == 0 ):
            computed_new_mdfe = 1
            self.compute_mdfe_values()
        if( computed_new_mdfe ):
            self.compute_max_mdfe_values()
        else:
            if( self.read_max_mdfe_values() == 0 ):
                print "computing max_mdfe_values"
                self.compute_max_mdfe_values()
        temp =  1.0-self.mdfe/self.max_mdfe
        #temp = self.max_mdfe-self.mdfe
        self.mdfe = 0
        self.max_mdfe = 0
        return temp
    except Exception, error:
        print "failed in fomf3 ", error
        sys.exit()
def compute_mdfe_values(fom, Nmax=20.0, view=0 ):
    """This function is an implementation of Dennis and Liang's algorithm for 
    computing what they refer to as the MDFE = 20*DFE(V_i)+N(V_i)
    where DFE(V_i) is the DFE at voxel V_i and N(V_i) is the number of neighbors of
    V_i which have the same DFE value as V_i)"""
    try:
    
        # For efficient tracking of neighbors use the mask dictionary
        
        if( self.read_mask_dictionary(get_dictionaries=[0,1]) == 0 ):
            print "Generating dictionary of neighborhood relationships"
            self.define_mask_dictionary(define_dictionaries=[1,1])
            self.save_mask_dictionary()
    
        # Create array for storing MDFE values
        self.mdfe = na.zeros(len(fom),na.float32)
        # the keys for self.Neighbors are just the indicies from 0 to Numpoints-1 
        #for key in self.Neighbors.keys():
        incr = len(self.fom) / 1000
        print "Computing MDFE values"
        for i in range(len(self.fom)):
            if( i % incr == 0 ):
                print "processing voxel ",i," of ",len(self.fom)
            val = self.fom_raw[i]
            nvals = len(Numeric.nonzero( Numeric.take(self.fom_raw,self.Neighbors[i]) == val ))	
            self.mdfe[i] = val + nvals/Nmax
        fo = open(self.maskfile+"_mdfe.pckle","wb")
        cPickle.dump([self.mdfe],fo,1)
        fo.close()
    except Exception, error:
        print "Failed in compute_mdfe_values ", error
def compute_max_mdfe_values( self ):
    """This function computes the local maximum DFE value following Liang"""
    try:
        self.max_mdfe = Numeric.zeros(len(self.fom),Numeric.Float32)
    
        # generate sorted indices into mdfe
    
        inds = Numeric.argsort( self.mdfe )[::-1]
    
        for ind in inds:
            nmax = MLab.max(Numeric.take(self.mdfe,self.Neighbors[ind]))
            self.max_mdfe[ind] = max(self.mdfe[ind],nmax)
        MyImageUtils.write_mimg(self.dim,self.inds,\
            self.max_mdfe,self.maskfile+"_maxmdfe.mimg")
        fo = open(self.maskfile+"_maxmdfe.pckle","wb")
        cPickle.dump([self.max_mdfe],fo,1)
        fo.close()
    except Exception, error:
        print "compute_max_mdfe_values ", error

