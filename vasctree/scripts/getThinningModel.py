#!/usr/bin/env python
from SkeletonGraph import *
def main():
    oimg = io.readImage(sys.argv[1],returnITK=False,imgMode = "sshort")
    tmp = os.path.splitext(sys.argv[1])
    pfile = tmp[0]+"greatOrigins.pckle"
    #a3d.call(data=[oimg], title="label pulmonary trunks",
             #labels=["leftPulmonaryTrunk","rightPulmonaryTrunk"],colors=["red","blue"],
             #AllowAddPoints=True, pointsFile=pfile, AllowDeletePoints=True)
    origins = cPickle.load(open(tmp[0]+"greatOrigins.pckle",'rb'))
    reader = itk.ImageFileReader.IUC3.New(FileName=sys.argv[2])
    filler = itk.VotingBinaryIterativeHoleFillingImageFilter.IUC3.New()
    filler.SetInput(reader.GetOutput())
    
    tmp2 = os.path.splitext(sys.argv[2])
    outFill = tmp2[0]+"_fill.mha"
    outSkel = tmp2[0]+"_fill_skel.mha"
    writer = itk.ImageFileWriter.IUC3.New()
    writer.SetInput(filler.GetOutput())
    writer.SetFileName(outFill)
    print("filling in holes in segmentation")
    writer.Update()
    subprocess.call("BinaryThinning3D %s %s"%(outFill,outSkel),shell=True)
    img = io.readImage(outSkel,returnITK=False,imgMode = "uchar")
    sg = SkeletonGraph(img)
    print("generating graph from skeleton")
    sg.getGraphFromSkeleton()
    for i in range(len(sg.graphs)):
        print("processing graph %d"%i)
        sg.setCurrentNumber(i)
        sg.setCurrentGraph()
        sg.findEndpointsBifurcations()
    fo = open(pfile,'rb')
    origins = cPickle.load(fo)
    sg.setRoots(origins)
    print("ordering graphs")
    for i in range(len(sg.graphs)):  
        sg.setCurrentNumber(i)
        sg.traceEndpoints()       
    
    sg.saveGraphs(tmp2[0]+"_graphs.pckle")
    sg.insertGraphInImage(oimg)
    a3d.call(data=[oimg])
if __name__ == '__main__':
    main()
