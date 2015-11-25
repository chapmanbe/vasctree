"""This code is responsible for making sure that the center point in slice 1 carries a value of 1 for each endpoint,
to be considered a valid endpoint and removes all those that do not meet that criteria."""
import sys
import pickle

fle=open("OrientedEndpoints7x7.pckle",  'rb')
data=pickle.load(fle)
out=open("CorrectedOrientedEndpoints7x7.pckle",  'wb')
length=len(data)
print("There are",  length,  "endpoints")
CorrectedPoints=[]
for d in data:    
    if d[3, 3, 3]==1:
        CorrectedPoints.append(d)
    else:
        print("invalid endpoint") 
        print(d)
print("There are now", len(CorrectedPoints), "endpoints")
pickle.dump(CorrectedPoints,  out)
