import VascTree

class VascTreeWx(VascTree.VascTree):
    def __init__(self):
        VascTree.VascTree.__init__(self) # Need to convert to a super call

        self.vzimg = None
        self.drawz = None
        self.vyimg = None
        self.drawy = None
        self.vximg = None
        self.drawx = None
        self.bw = False
        self.show = False
        self.colors = [(255,0,0),(255,64,0),(255,128,0),\
                      (255,255,0), (128,255,0),(64,255,0),(0,255,0),\
                      (0,255,64),(0,255,128),(0,255,255),(0,128,255),\
                      (0,64,255),(0,0,255),(64,0,255),(128,0,255),(255,0,255),\
                      (255,64,255),(255,128,255)]

        # Initialize wxImage handlers
        wx.wxInitAllImageHandlers()
        
    def __del__(self):
        self.vzimg = 0
        self.vyimg = 0
        self.vximg = 0

    def overlay_label(self,pnt,txt,color):
        """overlay a label at pnt"""
        try:
            self.drawz.text([self.scale[1]*(pnt[1]+0.5),\
                      self.scale[0]*(pnt[0]+0.5)],\
                      txt,fill=color)
            self.drawy.text([self.scale[2]*(pnt[2]+0.5),\
                      self.scale[0]*(pnt[0]+0.5)],\
                      txt,fill=color)
            self.drawx.text([self.scale[2]*(pnt[2]+0.5),\
                      self.scale[1]*(pnt[1]+0.5)],\
                      txt,fill=color)
        except Exception, error:
            print "failed in overlay_label()",error
    def overlay_point(self,pnt,color):
        """overlay the pnt on the x, y and z mips using color"""
        try:
            self.drawz.point([self.scale[1]*(pnt[1]+0.5),\
                      self.scale[0]*(pnt[0]+0.5)],\
                      fill=color)
            self.drawy.point([self.scale[2]*(pnt[2]+0.5),\
                      self.scale[0]*(pnt[0]+0.5)],\
                      fill=color)
            self.drawx.point([self.scale[2]*(pnt[2]+0.5),\
                      self.scale[1]*(pnt[1]+0.5)],\
                      fill=color)
        except Exception, error:
            print "failed in overlay_point()",error

    def draw_centered_box(self,p,s=1,color=(0,255,0)):
        try:
            sx = self.scale[0]
            sy = self.scale[1]
            sz = self.scale[2]
            self.drawz.rectangle([sy*(p[1]+0.5-s),sx*(p[0]+0.5-s),\
                                  sy*(p[1]+1.5+s),sx*(p[0]+1.5+s)],\
                                  fill=color,outline=color)
            self.drawy.rectangle([sz*(p[2]+0.5-s),sx*(p[0]+0.5-s),\
                                  sz*(p[2]+1.5+s),sx*(p[0]+1.5+s)],\
                                  fill=color,outline=color)
            self.drawx.rectangle([sz*(p[2]+0.5-s),sy*(p[1]+0.5-s),\
                                  sz*(p[2]+1.5+s),sy*(p[1]+1.5+s)],\
                                  fill=color,outline=color)
        except Exception, error:
            print "failed in draw_centered_box()",error
    def overlay_seeds(self, drawlabel=1):
        """overlay the detected seed points on the image"""
        try:
            if( self.bw == 'yes' ):
                s_color = (255,255,255)#(128,128,128)
            else:
                s_color = (255,0,255)
            seeds = self.get_crds(self.seeds)
            for i in range(len(self.seeds)):
                seed = seeds[i]
                self.draw_centered_box(seed,0.25,s_color)
                if( drawlabel):
                    self.overlay_label(seed,repr(i),s_color)
    
        except Exception, error:
            print "failed in overlay_seeds()",error
    

       
    def overlay_bifurcations(self):
        """overlay the detected bifurcation points"""
        try:
            inds = Numeric.array(self.bifurcations.keys())
            pnts = self.get_crds(inds)
            for i in range(pnts.shape[0]):
                pnt = pnts[i,:]
                self.draw_centered_box(pnt,0.25,(255,255,255))
        except Exception, error:
            print "failed in overlay_bifurcations()",error
    def initialize_draw_imgs(self):
        try:
            vimg = Numeric.zeros(self.dim[::-1],Numeric.Int8)
            if( MLab.max(self.vals) > 1e6):
                Numeric.put(vimg.flat,self.inds,self.vals < MLab.max(self.vals) )
            else:
                Numeric.put(vimg.flat,self.inds,1)
            
            zmip = self.zmip
            ymip = self.ymip
            xmip = self.xmip
            # set up zmip images
            print "set up zmip images"
            range  = MLab.max(zmip.flat)-MLab.min(zmip.flat)
            self.vzimg = MyImageUtils.ArrayToPilImage(\
                                zmip,win=range,\
                                lev=range/2).convert("RGB")
            self.vzimg = self.vzimg.transpose(\
                            Image.ROTATE_90).transpose(Image.FLIP_TOP_BOTTOM)
            sz = self.vzimg.size
            self.vzimg = self.vzimg.resize(\
                            (self.scale[0]*sz[0],self.scale[1]*sz[1]))
            self.drawz = ImageDraw.Draw(self.vzimg,mode="RGB")
            print "set up ymip images"
            # set up ymip images
            self.vyimg = MyImageUtils.ArrayToPilImage(\
                            ymip,win=range,lev=range/2).convert("RGB")
            self.vyimg = self.vyimg.transpose(\
                            Image.ROTATE_90).transpose(Image.FLIP_TOP_BOTTOM)
            sz = self.vyimg.size
            self.vyimg = self.vyimg.resize(\
                            (self.scale[0]*sz[0],self.scale[1]*sz[1]))
            self.drawy = ImageDraw.Draw(self.vyimg,mode="RGB")
            print "set up xmip images"
            # set up xmip images
            self.vximg = MyImageUtils.ArrayToPilImage(\
                        xmip,win=range,lev=range/2).convert("RGB")
            self.vximg = self.vximg.transpose(\
                        Image.ROTATE_90).transpose(Image.FLIP_TOP_BOTTOM)
            sz = self.vximg.size
            self.vximg = self.vximg.resize(\
                        (self.scale[0]*sz[0],self.scale[1]*sz[1]))
            self.drawx = ImageDraw.Draw(self.vximg,mode="RGB")
        except Exception, error:
            print "failed in initialize_draw_imgs()",error
            sys.exit()
    def display_voxel_map(self):
        try:
            self.initialize_draw_imgs()
            colors = [(255,255,255),(0,0,0),(255,0,0),(255,64,0),(255,128,0),\
                      (255,255,0), (128,255,0),(64,255,0),(0,255,0),\
                      (0,255,64),(0,255,128),(0,255,255),(0,128,255),\
                      (0,64,255),(0,0,255),(64,0,255),(128,0,255),(255,0,255),\
                      (255,64,255),(255,128,255)]
    
            maxseg = MLab.max(self.vmap)+1
            for s in range(1,maxseg+1):
                ind = Numeric.nonzero(self.vmap == s )
                inds = Numeric.take(self.map_inds,ind)
                pnts = Numeric.transpose(self.get_crds(inds))
                self.draw_points(pnts,color=colors[(s-1)%20])
            self.save_path_img(suffix="_vmaps.png")
    
        except Exception, error:
            print "failed iif( rflags.twod_flg != 1 )n display_voxel_map()", error



    def draw_points(self, points, color=(0,255,0)):
        try:
            ind1 = 2*Numeric.array((range(len(points[0]))))
            ind2 = ind1+1
            # zmip
            crds = Numeric.zeros(2*len(points[0]))
            Numeric.put(crds,ind1,self.scale[1]*(points[1]+0.5))
            Numeric.put(crds,ind2,self.scale[0]*(points[0]+0.5))
            self.drawz.point(crds,fill=color)
            # ymip
            crds = Numeric.zeros(2*len(points[0]))
            Numeric.put(crds,ind1,self.scale[2]*(points[2]+0.5))
            Numeric.put(crds,ind2,self.scale[0]*(points[0]+0.5))
            self.drawy.point(crds,fill=color)
            # xmip
            crds = Numeric.zeros(2*len(points[0]))
            Numeric.put(crds,ind1,self.scale[2]*(points[2]+0.5))
            Numeric.put(crds,ind2,self.scale[1]*(points[1]+0.5))
            self.drawx.point(crds,fill=color)
    
        except Exception, error:
            print "failed in draw_lines()",error
            sys.exit()

    def draw_path(self, points, color=(0,255,0)):
        try:
            ind1 = 2*Numeric.array((range(len(points[0]))))
            ind2 = ind1+1
            # zmip
            crds = Numeric.zeros(2*len(points[0]))
            Numeric.put(crds,ind1,self.scale[1]*(points[1]+0.5))
            Numeric.put(crds,ind2,self.scale[0]*(points[0]+0.5))
            self.drawz.line(crds,fill=color)
            # ymip
            crds = Numeric.zeros(2*len(points[0]))
            Numeric.put(crds,ind1,self.scale[2]*(points[2]+0.5))
            Numeric.put(crds,ind2,self.scale[0]*(points[0]+0.5))
            self.drawy.line(crds,fill=color)
            # xmip
            crds = Numeric.zeros(2*len(points[0]))
            Numeric.put(crds,ind1,self.scale[2]*(points[2]+0.5))
            Numeric.put(crds,ind2,self.scale[1]*(points[1]+0.5))
            self.drawx.line(crds,fill=color)
    
        except Exception, error:
            print "failed in draw_lines()",error
            sys.exit()

    def show_single_path(self, pathnum = 0, drawlabel = 1 ):
        try:
            self.initialize_draw_imgs()
            colors = [(255,255,255),(0,0,0),(255,0,0),(255,64,0),(255,128,0),\
                      (255,255,0), (128,255,0),(64,255,0),(0,255,0),\
                      (0,255,64),(0,255,128),(0,255,255),(0,128,255),\
                      (0,64,255),(0,0,255),(64,0,255),(128,0,255),(255,0,255),\
                      (255,64,255),(255,128,255)]
            path = self.paths[pathnum]
            pth = self.get_crds(path)
            if( drawlabel):
                mp = len(path)/2
                lcrd = [pth[mp,0],pth[mp,1],pth[mp,2]]
                if( self.bw == 'yes'):
                    self.overlay_label(lcrd,repr(pathnum),(0,0,0))
                else:
                    self.overlay_label(lcrd,repr(pathnum),colors[pathnum % 20])
                
            if( self.bw == 'yes' ):
                self.draw_path([pth[:,0],pth[:,1],pth[:,2]],(0,0,0))
            else:
                self.draw_path([pth[:,0],pth[:,1],pth[:,2]],
                                colors[pathnum % 20])
            self.save_path_img(suffix="_sp_"+repr(pathnum)+".png")

        except Exception, error:
            print "failed in show single path", error

    def draw_paths(self, minlength = 0, drawlabel = 0 ):
        try:
            self.initialize_draw_imgs()
            colors = [(255,255,255),(0,0,0),(255,0,0),(255,64,0),(255,128,0),\
                      (255,255,0), (128,255,0),(64,255,0),(0,255,0),\
                      (0,255,64),(0,255,128),(0,255,255),(0,128,255),\
                      (0,64,255),(0,0,255),(64,0,255),(128,0,255),(255,0,255),\
                      (255,64,255),(255,128,255)]
            count = 0
            for path in self.paths:
                if( len(path) > minlength ):
                    pth = self.get_crds(path)
                    if( drawlabel):
                        mp = len(path)/2
                        lcrd = [pth[mp,0],pth[mp,1],pth[mp,2]]
                        if( self.bw == 'yes'):
                            self.overlay_label(lcrd,repr(count),(0,0,0))
                        else:
                            self.overlay_label(lcrd,repr(count),
                                    colors[count % 20])
                
                    if( self.bw == 'yes' ):
                        self.draw_path([pth[:,0],pth[:,1],pth[:,2]],(0,0,0))
                    else:
                        self.draw_path([pth[:,0],pth[:,1],pth[:,2]],
                                    colors[count % 20])
                    count += 1
            if( self.show ):
                self.vzimg.show()
                self.vyimg.show()
                self.vximg.show()
        except Exception, error:
            print "failed in draw_paths()",error
            sys.exit()

    def draw_ordered_paths(self):
        try:
            self.initialize_draw_imgs()
            colors = [(255,255,255),(0,0,0),(255,0,0),(255,64,0),(255,128,0),\
                      (255,255,0), (128,255,0),(64,255,0),(0,255,0),\
                      (0,255,64),(0,255,128),(0,255,255),(0,128,255),\
                      (0,64,255),(0,0,255),(64,0,255),(128,0,255),(255,0,255),\
                      (255,64,255),(255,128,255)]
            for tkey in self.trees.keys():
                tree = self.trees[tkey]
                keys = self.tree.keys() 
                for key in keys:
                    seg = tree[key]
                    path = self.paths[seg.seg]
                    pth = self.get_crds(path)
                    if( self.bw == 'yes' ):
                        self.draw_path([pth[:,0],pth[:,1],pth[:,2]],(0,0,0))
                    else:
                        self.draw_path([pth[:,0],pth[:,1],pth[:,2]],colors[seg.level % 20])
            if( self.show ):
                self.vzimg.show()
                self.vyimg.show()
                self.vximg.show()
        except Exception, error:
            print "failed in draw_ordered_paths()",error
            sys.exit()

    def drawSegmentMap(self):
        try:
            self.initialize_draw_imgs()
            inds = Numeric.take(self.map_inds,ind)
            pnts = Numeric.transpose(self.get_crds(inds))
            self.draw_points(pnts,color=self.colors[(seg.seg)%18])
            # replace with a self.getColor(seg) function
            self.save_path_img(suffix="_"+repr(seg.seg)+"_vmaps.png")
        except:
            pass
    def draw_fit_ordered_paths(self,maxiter=5, display = 1):
        try:
            self.initialize_draw_imgs()
            for tkey in self.trees.keys():
                tree = self.trees[tkey]
                keys = tree.keys() 
                for key in keys:
                    seg = tree[key]
                    data = self.fit_path(self.paths[seg.seg],maxiter)
                    if( display ):
                        if( self.bw ):
                            self.draw_path(data[0],(0,0,0))
                        else:
                            self.draw_path(data[0],colors[seg.level % 20])
            
            if( self.show and display ):
                self.vzimg.show()
                self.vyimg.show()
                self.vximg.show()
        except Exception, error:
            print "failed in fit_ordered_paths()",error
            sys.exit()
    def save_val_img(self, data, suffix="_cf_zmip.png",\
             win=None,\
             lev=None,\
             view = 'z'):
        try:
            temp = Numeric.zeros(self.mask.shape,Numeric.Float32)
            Numeric.put(temp.flat,self.inds,data)
            if( view == 'z'):
                mimg = MLab.max(temp)
            elif( view == 'y'):
                mimg = MLab.max(temp,axis=1)
            else:
                mimg = MLab.max(temp,axis=2)
            timg = MyImageUtils.ArrayToPilImage(mimg,
                                win=win,lev=lev).convert("RGB")
            timg = timg.transpose(\
                    Image.ROTATE_90).transpose(Image.FLIP_TOP_BOTTOM)
            if( self.show ):
                timg.show()
            mimg = timg.tostring('raw',"RGB")
            imageWx = wx.wxEmptyImage(timg.size[0],timg.size[1])
            imageWx.SetData(mimg)
            imageWx.SaveFile(self.maskfile+self.vsuffix+suffix,wx.wxBITMAP_TYPE_PNG)
        except Exception, error:
            print "failed in save_val_img()",error
            sys.exit()


    def save_path_img(self, suffix="_fpaths.png"):
        try:
            if( self.show ):
                self.vzimg.show()
                self.vyimg.show()
                self.vximg.show()
                
            # zmip
            imageData = self.vzimg.tostring('raw','RGB')
            imageWx = wx.wxEmptyImage(self.vzimg.size[0],self.vzimg.size[1])
            imageWx.SetData(imageData)
            imageWx.SaveFile(self.maskfile+\
                "_zmip"+self.vsuffix+suffix,wx.wxBITMAP_TYPE_PNG)
            # ymip
            imageData = self.vyimg.tostring('raw','RGB')
            imageWx = wx.wxEmptyImage(self.vyimg.size[0],self.vyimg.size[1])
            imageWx.SetData(imageData)
            imageWx.SaveFile(self.maskfile+\
                "_ymip"+self.vsuffix+suffix,wx.wxBITMAP_TYPE_PNG)
            # xmip
            imageData = self.vximg.tostring('raw','RGB')
            imageWx = wx.wxEmptyImage(self.vximg.size[0],self.vximg.size[1])
            imageWx.SetData(imageData)
            imageWx.SaveFile(self.maskfile+\
                "_xmip"+self.vsuffix+suffix,wx.wxBITMAP_TYPE_PNG)
        except Exception, error:
            print "failed in save_path_img()",error
            sys.exit()
    def process_paths(self, read_data = 1, mode = 1, reverse= 1, gsanalysis = 'yes', dijkstra = 'yes'):
        try:
            print "process_paths() arguments ", read_data, mode, reverse, gsanalysis, dijkstra
            if( read_data ):
                print "reading data"
                self.load_data(rpaths=0,fpaths=0)
            self.read_gs_points()
            self.draw_paths()
            self.save_path_img(suffix="_nonpruned_opths.png")
            self.initialize_draw_imgs()
            self.overlay_seeds()
            self.save_path_img(suffix="_seeds.png")
    
            self.prune_paths()
            self.draw_paths(drawlabel=1)
            self.save_path_img(suffix="_raw_opths.png")
            for i in range(10):
                self.show_single_path(pathnum=i)
    
            self.split_paths()
            self.draw_paths()
            self.save_path_img(suffix="_split_opths.png")
            if( (mode == 2 or mode == 3) and reverse):
                self.reverse_paths()
                self.draw_paths()
                self.save_path_img(suffix="_reverse_opths.png")
            self.order_tree()
            self.compute_descendents()
            self.save_path_data()
            self.draw_paths(drawlabel=1)
            #self.draw_ordered_paths()
            self.overlay_bifurcations()
            self.save_path_img(suffix="_opaths.png")
            self.fit_ordered_paths()
            self.save_fit_paths()
            self.get_path_lengths()
            self.overlay_bifurcations()
            if( gsanalysis == 'yes' ):
                self.overlay_gs_bifurcations()
            self.save_path_img()
            self.print_trees()
        except Exception, error:
            print "failed in process_paths()",error
            sys.exit()

