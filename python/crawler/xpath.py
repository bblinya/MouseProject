
str_strip = "translate(text(), ' &#9;&#10;&#13', '')"
str_len = "string-length({})".format(str_strip)

def in_cls(*args):
    return " or ".join([
        "contains(@class, '%s')" % s for s in args])

def in_ids(*args):
    return " or ".join([
        "contains(@id, '%s')" % s for s in args])

def ex(*args):
    return " or ".join(args)
