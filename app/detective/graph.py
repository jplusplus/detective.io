import re

# Extract node id from given node uri
def node_id(uri):
    return int( re.search(r'(\d+)$', uri).group(1) )

# Get the end of the given relationship
def rel_from(rel, side):
    return node_id(rel._dic[side])

# Is the given relation connected to the given idx
def connected(rel, idx):
    return rel_from(rel, "end") == idx or rel_from(rel, "start") == idx

# Get the opposite node id according the given relationship
def opposite(rel, idx):
    side = "start" if rel_from(rel, "end") == idx else "end"
    return rel_from(rel, side)