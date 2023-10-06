
str_strip = "translate(text(), ' &#9;&#10;&#13', '')"

def str_len(val = str_strip):
    return "string-length({})".format(val)

def idx_range(start=None, stop=None):
    """ index start from 1 """
    pat = []
    start and pat.append("position() > %i" % start)
    stop and pat.append("position() < %i" % stop)
    return " and ".join(pat)

def in_cls(*args):
    return " or ".join([
        "contains(@class, '%s')" % s for s in args])

def in_ids(*args):
    return " or ".join([
        "contains(@id, '%s')" % s for s in args])

def ex(*args):
    return " or ".join(args)
