def cf1(fom, dist, source):
    try:
        newvals = fom*dist+source
        return newvals
    except Exception as error:
        print("failed in cf1()",error)
        sys.exit()

