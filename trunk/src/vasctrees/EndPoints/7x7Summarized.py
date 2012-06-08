#7x7Summarized.py

"""This purpose of this code is to summarize all of the Endpoints.pckle the
output of the 7x7 neighbors into 1 file"""
import sys
import cPickle
import numpy as na
sys.path.append("../../../../../../Desktop/7x7SummaryFiles")
def main():
    files=["PE00001Endpoints7x7.pckle","PE00002Endpoints7x7.pckle",
           "PE00004Endpoints7x7.pckle", "PE00006Endpoints7x7.pckle",
           "PE00007Endpoints7x7.pckle","PE00009Endpoints7x7.pckle",
           "PE00010Endpoints7x7.pckle","PE00011Endpoints7x7.pckle",
           "PE00012Endpoints7x7.pckle", "PE00014Endpoints7x7.pckle",
           "PE00016Endpoints7x7.pckle",  "PE00017Endpoints7x7.pckle",
           "PE00018Endpoints7x7.pckle",  "PE00021Endpoints7x7.pckle",
           "PE00023Endpoints7x7.pckle",  "PE00024Endpoints7x7.pckle",
           "PE00025Endpoints7x7.pckle", "PE00026Endpoints7x7.pckle"  ]
    output=open("7x7Summary.pckle",'wb')
    
    Sum=[]
    for f in files:
        f1=open(f)
        f2=cPickle.load(f1)
        print f2[3,3,3]
        count += f2[3,3,3]
        Sum.append(f2)
    start=Sum[0]
    for s in Sum:
        start +=s
    cPickle.dump(start,  output)
if __name__=='__main__':
    main()
