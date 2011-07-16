#7x7NonEndpointSummarized.py

"""This purpose of this code is to summarize all of the img#Points7x7.pckle
the output of the 5x5neighbors into 1 file"""
import sys
import cPickle
import numpy as na
sys.path.append("../../../../../../Desktop/7x7NonEndpointSummaryFiles")
def main():
    files=["PE00001Points7x7.pckle","PE00002Points7x7.pckle",
           "PE00004Points7x7.pckle", "PE00006Points7x7.pckle",
           "PE00007Points7x7.pckle","PE00009Points7x7.pckle",
           "PE00010Points7x7.pckle","PE00011Points7x7.pckle",
           "PE00012Points7x7.pckle", "PE00014Points7x7.pckle",
           "PE00016Points7x7.pckle",  "PE00017Points7x7.pckle",
           "PE00018Points7x7.pckle",  "PE00021Points7x7.pckle",
           "PE00023Points7x7.pckle",  "PE00024Points7x7.pckle",
           "PE00025Points7x7.pckle", "PE00026Points7x7.pckle"  ]
    output=open("7x7NonEndpointsSummary.pckle",'wb')
    Sum=[]
    count=0
    for f in files:
        f1=open(f)
        f2=cPickle.load(f1)
        print f2[3, 3, 3]
        count += f2[3, 3, 3]
        Sum.append(f2)
    start=Sum[0]
    for s in Sum[1:]:
        start +=s
    print "total number of points is %d"%count
    cPickle.dump(start,  output)
if __name__=='__main__':
    main()
