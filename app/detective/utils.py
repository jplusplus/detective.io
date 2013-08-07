import re

def to_class_name(value=""):
    """
    Class name must:
        - begin by an uppercase
        - use camelcase
    """
    value = to_camelcase(value)
    value = list(value)
    if len(value) > 0:
        value[0] = value[0].capitalize()

    return "".join(value)


def to_camelcase(value=""):

    def camelcase(): 
        yield str.lower
        while True:
            yield str.capitalize            

    value =  re.sub(r'([a-z])([A-Z])', r'\1_\2', value)
    c = camelcase()
    return "".join(c.next()(x) if x else '_' for x in value.split("_"))

def to_underscores(value=""):    
    # Lowercase of the first letter
    value = list(value)
    if len(value) > 0:
        value[0] = value[0].lower()
    value = "".join(value)

    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', value)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()