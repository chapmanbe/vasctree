from scipy import weave

def search1(a,b):
    try:
        code = """
        int mb = b.length() ; int ma = a.length() ;
        for( int i = 0; i < mb ; i++ ){
            for( int j = 0; j < ma ; j++){
                if( b[i] == a[j] ){
                    return_val = py::new_reference_to(Py::Int(j));
                    printf("%d",j);
                    break;
                }
            }
        }"""

        print weave.inline(code,['a','b'])
    except Exception, error:
        print "failed in search1",error
