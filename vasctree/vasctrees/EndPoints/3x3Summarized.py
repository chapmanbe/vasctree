"""This purpose of this code is to summarize all of the Endpoints.pckle the
output of the 3x3 neighbors into 1 file"""
import sys
import cPickle
import numpy as na
sys.path.append("../../../../../Desktop/3x3SummaryFiles")
def main():
    files=["PE00001Endpoints.pckle","PE00002Endpoints.pckle",
           "PE00004Endpoints.pckle", "PE00006Endpoints.pckle",
           "PE00007Endpoints.pckle","PE00009Endpoints.pckle",
           "PE00010Endpoints.pckle","PE00011Endpoints.pckle",
           "PE00012Endpoints.pckle", "PE00014Endpoints.pckle",
           "PE00016Endpoints.pckle",  "PE00017Endpoints.pckle",
           "PE00018Endpoints.pckle",  "PE00021Endpoints.pckle",
           "PE00023Endpoints.pckle",  "PE00024Endpoints.pckle",
           "PE00025Endpoints.pckle", "PE00026Endpoints.pckle"  ]
    output=open("3x3Summary.pckle",'wb')
    Sum=[]
    count = 0
    for f in files:
        f1=open(f)
        f2=cPickle.load(f1)
        print f2[1,1,1]
        count += f2[1,1,1]
        Sum.append(f2)
    start=Sum[0]
    for s in Sum[1:]:
        start +=s
    cPickle.dump(start,  output)
    print "total number of points is %d"%count
if __name__=='__main__':
    main()
