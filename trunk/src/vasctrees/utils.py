"""**vasctrees.utils**: A set of utilities common to multiple vasctree scripts and packages

Defined functions include:

+ getOrderedGraphKeys

+ readGraphs

+ writeGraphs

"""
import gzip
import cPickle
def getOrderedGraphKeys(ogs):
    """
    This is a utility function to list the keys of a graph dictionary and prompt the user to select a particular graph from the dictionary
    """
    keys = ogs.keys()
    txt = "Select number of desired key:\n"
    for i in range(len(keys)):
        txt += """%d\t\t%s\n"""%(i,keys[i])
    while(True):
        try:
            keyNum = input(txt)
            if( 0 <= keyNum and keyNum < len(keys) ):
                return keys[keyNum]
        except:
            pass
    return None
def readGraphs(fname):
    """
    reads a pickled SkeletonGraph file. Initially tries to read it in assuming in has
    been compressed with gzip. If this fails then it proceeds to try to read the Pickle archives as a normal file.

    **Arguments:**
    *fname*: filename to read graphs from


    """
    try:
        fo = gzip.open(fname,"rb")
        data = cPickle.load(fo)
        fo.close()
    except:
        fo = file(fname,"rb")
        data = cPickle.load(fo)
        fo.close()
    return data
def writeGraphs(data,fname):
    """
    writes a pickled SkeletonGraph file to a gzipped file.

    **Arguments:**

    *data*: the dictionary of SkeletonGraph data
    *fname*: the file name to write to
    """

    fo = gzip.open(fname,"wb")
    cPickle.dump(data,fo)
    fo.close()

