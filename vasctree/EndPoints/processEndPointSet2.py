"""This code summarized the corrected endpoints after those that were 
proved invalid by Endpointcheck.py were removed"""
import sys
import pickle
import numpy as na

def main():
    fle=open("CorrectedOrientedEndpoints.pckle",'rb') 
    data = pickle.load(fle)
    output=open("Endpoints.pckle",  'wb')
    target = data[0]
    count=0
    for d in data[1:]:
        count+=1
        print(count)
        target += d
    print(target)
    pickle.dump(target,  output)

    
if __name__ == '__main__':
    main()
