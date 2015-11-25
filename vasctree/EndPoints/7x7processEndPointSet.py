"""takes the output from 7x7Config_of_Endpoints.py and returns Orientedendpoints7x7.pckle. 
The main purpose of this code is to make sure the the endpoints are aligned in the same 
direction for the 7x7neighborhood, to be sure they are all rotationally invariant"""

from sliceOrientation import OrientMask
import sys
import pickle
import numpy as na

def main():
    fle=open("Configuration7x7.pckle",'rb') 
    data = pickle.load(fle)
    output=open("OrientedEndpoints7x7.pckle",  'wb')
    modifiedEp = []
    count=0
    remove=[]
    print("%d endpoints"%len(data[0]))
    for ep in data[0]:
        count +=1
        if len(ep)<7:
            pass
        else:
            om = OrientMask(ep)
            om.orient()
            modifiedEp.append(om.mask) 
    pickle.dump(modifiedEp , output)
    
if __name__ == '__main__':
    main()
