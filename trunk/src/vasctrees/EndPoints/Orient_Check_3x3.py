##Orient_Check_3x3.py

"""Replacing processEndpointSet.py and endpointCheck.py, Originally only the neighborhoods were returned
in CorrectedOrientedEndpoints.pckle needed to go back and grab the crds"""

from sliceOrientation import OrientMask
import sys
import cPickle
import numpy as na

def main():
    fle=open("Configuration.pckle",'rb') 
    data = cPickle.load(fle)
    output=open("CorrectedOrientedEndpoints.pckle",  'wb')
    out=open("crds.pckle",  "wb")
    modifiedEp = []
    coordinates=[]
    crds=[]
    counts=[]
    counts1=[]
    print "%d endpoints"%len(data[0])
    count=0
    for d in data[0]:
        count+=1
        if len(d)<3:
            print "Removed", count
            counts.append(count)
            print d
            pass
        else:
            om = OrientMask(d)
            om.orient()
            modifiedEp.append(om.mask) 
    length= len(modifiedEp)
    print "Endpoints",  counts,  "to be removed from crds"
    print "There are now",  length,  "endpoints"
    crdcount=0
    for d in data[1]:
        coordinates.append(d)
    CorrectedPoints=[]
    count1=0
    for mep in modifiedEp:    
        count1+=1
        if mep[1, 1, 1]==1:
            CorrectedPoints.append(mep)
        else:
            print count1
            counts1.append(count1)
            print "invalid endpoint" 
            print mep
    print "There are now", len(CorrectedPoints), "endpoints"
    print "Endpoints",  counts1,  "to be removed from crds"
    print "length of coordinates",  len(coordinates)
    crdscount=0
    removed=[]
    """The following section was modified for each image to take the values 
    found in counts 1 and replace in line crdscount==(Some number). To remove
    the correct coordinates and create a second file to store the locations"""
    for crd in coordinates:
        crdscount+=1
        if crdscount==6:
            removed.append(crd)
        elif crdscount==7:
            removed.append(crd)     
        elif crdscount==17:
            removed.append(crd)           
        elif crdscount==52:
            removed.append(crd)      
        elif crdscount==59:
            removed.append(crd)
        elif crdscount==76:
            removed.append(crd)
        elif crdscount==79:
            removed.append(crd)
        elif crdscount==80:
            removed.append(crd)
        elif crdscount==82:
            removed.append(crd)
        elif crdscount==83:
            removed.append(crd)
        elif crdscount==84:
            removed.append(crd)
        else:
            crds.append(crd)
    print "There are now", len(crds), "coordinates"
    cPickle.dump(CorrectedPoints,   output)  
    cPickle.dump(crds,  out)
if __name__ == '__main__':
    main()
