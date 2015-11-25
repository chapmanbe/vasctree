"""vasctrees.utils: A set of utilities common to multiple vasctree scripts and packages

Defined functions include:

+ getOrderedGraphKeys

+ readGraphs

+ writeGraphs

"""
import gzip
import pickle
def getOrderedGraphKeys(ogs):
    """
    This is a utility function to list the keys of a graph dictionary and prompt the user to select a particular graph from the dictionary
    """
    keys = list(ogs.keys())
    txt = "Select number of desired key:\n"
    for i in range(len(keys)):
        txt += """%d\t\t%s\n"""%(i,keys[i])
    while(True):
        try:
            keyNum = eval(input(txt))
            if( 0 <= keyNum and keyNum < len(keys) ):
                return keys[keyNum]
        except:
            pass
    return None
def readGraphs(fname):
    """Fetches graph data from file.
    
    Returns a SkeletonGraph data dictionary from a file. It first tries to
    read the file as a gzipped file. If this fails it tries to read it as a
    normal pickle file stored in a binary format.
    
    Args:
        fname: The file to read from
        
    Returns:
        A dict of the SkeletonGraph data. key/value pairs are as follows:
            'imgShape'/the tuple of the numpy array shape that the graphs 
                       were generated from
            'skelGraphs':dictionary of unordered graphs generated from the 
                         skeleton image. Graphs are ordered by object size.
            'orderedGraphs': dictionary of ordered graphs created by the user.
            'roots': dictionary of roots associated with each ordered graph.

    """
    try:
        fo = gzip.open(fname,"rb")
        data = pickle.load(fo)
        fo.close()
    except:
        fo = file(fname,"rb")
        data = pickle.load(fo)
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
    pickle.dump(data,fo)
    fo.close()

