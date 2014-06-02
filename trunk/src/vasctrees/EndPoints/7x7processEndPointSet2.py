"""This code summarized the corrected endpoints after those that were 
proved invalid by Endpointcheck7x7.py were removed"""
import sys
import cPickle
import numpy as na

def main():
    fle=open("CorrectedOrientedEndpoints7x7.pckle",'rb') 
    data = cPickle.load(fle)
    output=open("Endpoints7x7.pckle",  'wb')
    target = data[0]
    for d in data[1:]: 
        target += d
    cPickle.dump(target,  output)
    
if __name__ == '__main__':
    main()
