#AddNeighbors.py

import cPickle
"""To summarize the 112 neighborhoods for each 3x3,
5x5 and 7x7 for each image"""
#The input and output were adjusted for each image
#and each neighborhood
input=open("PE00001NeighborsNonPoints3x3.pckle", 'rb')
neighbors=cPickle.load(input)
output=open("PE00001Points3x3.pckle", "wb") 
count=neighbors[0]
for neighbor in neighbors[1:]:
    count +=neighbor
cPickle.dump(count,output)
    
