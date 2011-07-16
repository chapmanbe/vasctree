#5x5Summarized.py

"""This purpose of this code is to summarize all of the Endpoints5x5.pckle
the output of the 3x3 neighbors into 1 file"""
import sys
import cPickle
import numpy as na
sys.path.append("../../../../../../Desktop/5x5SummaryFiles")
def main():
    files=["PE00001Endpoints5x5.pckle","PE00002Endpoints5x5.pckle",
           "PE00004Endpoints5x5.pckle", "PE00006Endpoints5x5.pckle",
           "PE00007Endpoints5x5.pckle","PE00009Endpoints5x5.pckle",
           "PE00010Endpoints5x5.pckle","PE00011Endpoints5x5.pckle",
           "PE00012Endpoints5x5.pckle", "PE00014Endpoints5x5.pckle",
           "PE00016Endpoints5x5.pckle",  "PE00017Endpoints5x5.pckle",
           "PE00018Endpoints5x5.pckle",  "PE00021Endpoints5x5.pckle",
           "PE00023Endpoints5x5.pckle",  "PE00024Endpoints5x5.pckle",
           "PE00025Endpoints5x5.pckle", "PE00026Endpoints5x5.pckle"  ]
    output=open("5x5Summary.pckle",'wb')
    Sum=[]
    count=0
    for f in files:
        f1=open(f)
        f2=cPickle.load(f1)
        print f2[2, 2, 2]
        count += f2[2, 2, 2]
        Sum.append(f2)
    start=Sum[0]
    for s in Sum[1:]:
        start +=s
    print "total number of points is %d"%count
    cPickle.dump(start,  output)
if __name__=='__main__':
    main()
