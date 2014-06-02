#processendpointSet2_5x5.py

"""This code summarized the corrected endpoints after those that were 
proved invalid by Endpointcheck5x5.py were removed"""
import sys
import cPickle
import numpy as na

def main():
    fle=open("CorrectedOrientedEndpoints5x5.pckle",'rb') 
    data = cPickle.load(fle)
    output=open("Endpoints5x5.pckle",  'wb')
    target = data[0]
    for d in data[1:]:
        target += d
    cPickle.dump(target,  output)
    
if __name__ == '__main__':
    main()
