#endpointcheck5x5.py

"""This code is responsible for making sure that the center point in
carries a value of 1 for each endpoint,to be considered a valid endpoint
and removes all those that do not meet that criteria."""
import sys
import cPickle

fle=open("OrientedEndpoints5x5.pckle",  'rb')
data=cPickle.load(fle)
out=open("CorrectedOrientedEndpoints5x5.pckle",  'wb')
length=len(data)
print "There are",  length,  "endpoints"
CorrectedPoints=[]
for d in data:    
    if d[2, 2, 2]==1:
        CorrectedPoints.append(d)
    else:
        print "invalid endpoint" 
        print d
print "There are now", len(CorrectedPoints), "endpoints"
cPickle.dump(CorrectedPoints,  out)
