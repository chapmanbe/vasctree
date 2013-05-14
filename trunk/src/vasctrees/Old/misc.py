# Functions currently trimmed from main VascTree class    
#    def find_endpoints(self, limit = 1e20):
#        try:
#            print "Finding endpoints in cost function"
#            # drop points that were not connected
#            # use only points that lie on the edge of the mask
#            tind = na.array(range(len(self.vals)),na.int32)
#            vind = na.nonzero((self.vals < limit) * (self.fom_raw == 1))
#            tind = na.take(tind,vind)
#    
#            inds = na.take(self.inds,vind) 
#            tempvals = na.take(self.vals,vind)
#            tempfom_raw = na.take(self.fom_raw,vind)
#            pnts = self.get_crds(inds)
#            self.ends = []
#            temp1 = na.zeros(self.dim[::-1],na.int8)
#            temp2 = na.zeros(self.dim[::-1],na.int8)
#            na.put(temp2.flat,self.inds,127)
#            fo1 = open(self.__maskfile+"cf_max.txt","w")
#            #fo2 = open(self.__maskfile+"fom_max.txt","w")
#            nump = pnts.shape[0]
#            interval = nump / 100
#            for i in range(pnts.shape[0]):
#                if( i % interval == 0 ):
#                    print "processing point ",i," of ",nump
#                p = pnts[i,:]
#                vi = int(100*tempvals[i])
#                fomi = int(100*tempfom_raw[i])
#                # get new crds within image bounds
#                cx,cy,cz,dst,inds = apply(self.epn,(p,))
#                vals = na.take(self.vals,inds)
#                fom = na.take(self.fom_raw,inds)
#                if( vi > int(100*na.max(vals))):
#                    temp1[p[2],p[1],p[0]]=1
#                    fo1.write(repr(p)+"\n")
#                    self.ends.append(tind[i])
#            fo1.close()
#                
#            self.ends = na.array(self.ends)
#            evals = na.take(self.vals,self.ends)
#            self.ends = (na.take(self.ends,na.argsort(evals)))[-1::-1]
#            print len(self.ends), " end points found: local max"
#            view.view2DImage(self.zmip+255*na.max(temp1)) # Add necessary arguments
#            return self.ends
#        except Exception, error:
#            print "failed in find_endpoints ", error
#            sys.exit()
#            
#    def find_surface_points(self, surf_def=1):
#        try:
#            vind = na.nonzero(self.fom_raw == surf_def)
#            print "find_surface_points",len(vind),na.max(vind),len(self.inds),len(self.fom_raw)
#            self.sinds = na.take(self.inds,vind)
#        except Exception, error:
#            print "Failed in find_surface_points() ", error
#            sys.exit()
#
#
#    def get_path_lengths(self):
#        """ for each path in self.paths compute the length (number of 
#            voxels in the path)"""
#        try:
#            total_length = 0
#            for path in self.paths:
#                total_length += path.shape[0]
#            print "total path lengths = ",total_length
#        except Exception, error:
#            print "failed in get_path_lengths()",error
#            sys.exit()
#    def traceBackGraph(self):
#	"""How we find the path with lowest cost"""
#        #try:
#
#            # use nx.connected_component_subgraphs to grab the Graph components
#	print "+++++ traceBackMask++++++"
#	H=nx.connected_component_subgraphs(self.G)[0]
#	sources = H.copy()
#	Tree = nx.Graph()
#	target = self.getGraphTarget(H)
#
#	while( sources ):
#	    source = nx.distance.periphery(sources)[0]
#	    sources.remove_node(target)
#	    # do I want to use nx.bidirectional_dijksta which stores a tuple of two dictionaries keyed by node.
#	    # The 1st dict stores the distance form the source, the 2nd stores the path from the 
#	    #source to that node.
#	    # or nx.dijkstra_path which returns the shortest path from source to target in a weighted graph
#	    # uses the bidirectional version of dijkstra.
#
#	    path = nx.dijkstra_path(H,sources)
#
#	    path = set(path).difference(Tree.nodes())
#
#	    sources.remove_nodes_from(path)
#
#	    Tree.add_edge(target,source,path)
#
#        #except Exception, error:
#            #print "failed in traceBackGraph()", error
#            #sys.exit()
#           
#    def fill_mask_paths(self):
#
#        try:
#
#            temp = na.zeros(self.mask.shape,na.int16)
#
#            na.put(temp.flat,self.inds,1) # how do I define self.inds?
#
#            for path in self.paths:
#
#                inds = self.get_ind(path[:,0],path[:,1],path[:,2])
#
#                na.put(temp.flat,inds,na.take(temp.flat,inds)+1)
#
#            io.writeImage(temp,fname=self.__maskfile+"_paths.mha", inMode='int16')
#
#        except Exception, error:
#
#            print "failed in fill_mask_paths()",error
#
#            sys.exit()
