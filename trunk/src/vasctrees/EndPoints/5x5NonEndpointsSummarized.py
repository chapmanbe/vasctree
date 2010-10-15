#5x5NonEndpointSummarized.py

"""This purpose of this code is to summarize all of the img#Points5x5.pckle
the output of the 5x5neighbors into 1 file"""
import sys
import cPickle
import numpy as na
sys.path.append("../../../../../../Desktop/5x5NonEndpointSummaryFiles")
def main():
    files=["PE00001Points5x5.pckle","PE00002Points5x5.pckle",
           "PE00004Points5x5.pckle", "PE00006Points5x5.pckle",
           "PE00007Points5x5.pckle","PE00009Points5x5.pckle",
           "PE00010Points5x5.pckle","PE00011Points5x5.pckle",
           "PE00012Points5x5.pckle", "PE00014Points5x5.pckle",
           "PE00016Points5x5.pckle",  "PE00017Points5x5.pckle",
           "PE00018Points5x5.pckle",  "PE00021Points5x5.pckle",
           "PE00023Points5x5.pckle",  "PE00024Points5x5.pckle",
           "PE00025Points5x5.pckle", "PE00026Points5x5.pckle"  ]
    output=open("5x5NonEndpointsSummary.pckle",'wb')
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
