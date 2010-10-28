# Display the data #############################################################
from enthought.mayavi import mlab
import numpy as np

def viewImgWithNodes(img, spacing, contours,g, title=''):

    mlab.figure(bgcolor=(0, 0, 0), size=(400, 400))
    
    src = mlab.pipeline.scalar_field(img)
    # Our data is not equally spaced in all directions:
    src.spacing = [1, 1, 1]
    src.update_image_data = True

    mlab.pipeline.iso_surface(src, contours=contours, opacity=0.5)
    nodes = np.array(g.nodes())
    #mlab.points3d(nodes[:,0],nodes[:,1],nodes[:,2],color=(0.0,1.0,0.0))
    mlab.points3d(nodes[:,2],nodes[:,1],nodes[:,0],color=(0.0,0.0,1.0))
    
    for n1, n2, edge in g.edges(data=True):
        path = [n1]+edge['path']+[n2]
        pa = np.array(path)
        #print pa
        mlab.plot3d(pa[:,2],pa[:,1],pa[:,0],color=(0,1,0),tube_radius=0.25)
    mlab.view(-125, 54, 'auto','auto')
    mlab.roll(-175)
    mlab.title(title, height=0.1)
    
    mlab.show()
    
def viewImg2(img, spacing, contours):
    print "In viewImg2: (min,max)=(%f,%f)"%(img.min(),img.max())
    print "contours=",contours
    mlab.figure(bgcolor=(0, 0, 0), size=(400, 400))
    
    src = mlab.pipeline.scalar_field(img)
    # Our data is not equally spaced in all directions:
    src.spacing = [1, 1, 1]
    src.update_image_data = True
    
    
    # Extract some inner structures: the ventricles and the inter-hemisphere
    # fibers. We define a volume of interest (VOI) that restricts the
    # iso-surfaces to the inner of the brain. We do this with the ExtractGrid
    # filter.
    blur = mlab.pipeline.user_defined(src, filter='ImageGaussianSmooth')
    #mlab.pipeline.volume(blur, vmin=0.2, vmax=0.8)
    mlab.pipeline.iso_surface(src, contours=contours)
    #mlab.pipeline.image_plane_widget(blur,
    #                            plane_orientation='z_axes',
    #                            slice_index=img.shape[0]/2,
    #                        )
    #voi = mlab.pipeline.extract_grid(blur)
    #voi.set(x_min=125, x_max=193, y_min=92, y_max=125, z_min=34, z_max=75)
    
    #mlab.pipeline.iso_surface(src, contours=[1,2], colormap='Spectral')
    #mlab.pipeline.contour3d(blur)
        
    mlab.view(-125, 54, 'auto','auto')
    mlab.roll(-175)
    
    mlab.show()

def viewImg(img, spacing, contours):
    mlab.figure(bgcolor=(0, 0, 0), size=(400, 400))
    
    src = mlab.pipeline.scalar_field(img)
    # Our data is not equally spaced in all directions:
    src.spacing = [1, 1, 1]
    src.update_image_data = True
    
    
    # Extract some inner structures: the ventricles and the inter-hemisphere
    # fibers. We define a volume of interest (VOI) that restricts the
    # iso-surfaces to the inner of the brain. We do this with the ExtractGrid
    # filter.
    blur = mlab.pipeline.user_defined(blur, filter='ImageGaussianSmooth')
    print "blur type is",type(blur),blur.max()
    #voi = mlab.pipeline.extract_grid(blur)
    #voi.set(x_min=125, x_max=193, y_min=92, y_max=125, z_min=34, z_max=75)
    
    #mlab.pipeline.iso_surface(src, contours=[1,2], colormap='Spectral')
    mlab.pipeline.contour3d(blur)
        
    mlab.view(-125, 54, 'auto','auto')
    mlab.roll(-175)
    
    mlab.show()