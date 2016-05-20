"""
vasctrees.utils: A set of utilities common to multiple vasctree
scripts and packages

Defined functions include:

+ get_ordered_graph_keys

+ readGraphs

+ writeGraphs

"""
import gzip
import pickle
import networkx as nx


def get_ordered_graph_keys(ogs):
    """
    This is a utility function to list the keys of a graph dictionary
    and prompt the user to select a particular graph from the dictionary
    """
    keys = list(ogs.keys())
    txt = "Select number of desired key:\n"
    for i in range(len(keys)):
        txt += """%d\t\t%s\n"""%(i, keys[i])
    while True:
        try:
            keyNum = eval(input(txt))
            if 0 <= keyNum and keyNum < len(keys):
                return keys[keyNum]
        except:
            pass
    return None


def read_graphs(fname):
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
        with gzip.open(fname, "rb") as fo:
            try:
                data = pickle.load(fo, encoding="latin1")
            except TypeError:
                data = pickle.load(fo)
    except:
        with open(fname, "rb") as fo:
            try:
                data = pickle.load(fo, encoding="latin1")
            except TypeError:
                data = pickle.load(fo)
    return data


def write_graphs(data, fname):
    """
    writes a pickled SkeletonGraph file to a gzipped file.

    **Arguments:**

    *data*: the dictionary of SkeletonGraph data
    *fname*: the file name to write to
    """
    try:
        nx.write_gpickle(data, fname)
    except:
        with gzip.open(fname, "wb") as fo:
            pickle.dump(data, fo)
