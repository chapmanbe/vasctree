#3x3NonEndpointSummarized.py

"""This purpose of this code is to summarize all of the img#Points3x3.pckle
the output of the 3x3neighbors into 1 file"""
import sys
import pickle
import numpy as na
sys.path.append("../../../../../../Desktop/3x3NonEndpointSummaryFiles")
def main():
    files=["PE00001Points3x3.pckle","PE00002Points3x3.pckle",
           "PE00004Points3x3.pckle", "PE00006Points3x3.pckle",
           "PE00007Points3x3.pckle","PE00009Points3x3.pckle",
           "PE00010Points3x3.pckle","PE00011Points3x3.pckle",
           "PE00012Points3x3.pckle", "PE00014Points3x3.pckle",
           "PE00016Points3x3.pckle",  "PE00017Points3x3.pckle",
           "PE00018Points3x3.pckle",  "PE00021Points3x3.pckle",
           "PE00023Points3x3.pckle",  "PE00024Points3x3.pckle",
           "PE00025Points3x3.pckle", "PE00026Points3x3.pckle"  ]
    output=open("3x3NonEndpointsSummary.pckle",'wb')
    Sum=[]
    count=0
    for f in files:
        f1=open(f)
        f2=pickle.load(f1)
        print(f2[1, 1, 1])
        count += f2[1, 1, 1]
        Sum.append(f2)
    start=Sum[0]
    for s in Sum[1:]:
        start +=s
    print("total number of points is %d"%count)
    pickle.dump(start,  output)
if __name__=='__main__':
    main()
