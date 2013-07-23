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