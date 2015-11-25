#processEndpointSet.py

"""takes the output from 5x5Config_of_Endpoints.py and returns Orientedendpoints5x5.pckle. 
The main purpose of this code is to make sure the the endpoints are aligned in the same 
direction for the  5x5 neighborhood, to be sure they are all rotationally invariant"""

from sliceOrientation import OrientMask
import sys
import pickle
import numpy as na

def main():
    fle=open("Configuration.pckle",'rb') 
    data = pickle.load(fle)
    output=open("OrientedEndpoints.pckle",  'wb')
    modifiedEp = []
    """The original code used barring any exceptions"""
    print("%d endpoints"%len(data[0]))
    for ep in data[0]:
        if len(ep)<3:
            pass
        else:
            om = OrientMask(ep)
            om.orient()
            modifiedEp.append(om.mask) 
    print(len(modifiedEp))
    pickle.dump(modifiedEp, output)

    
if __name__ == '__main__':
    main()
