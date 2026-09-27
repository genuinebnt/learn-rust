`Graph` stores each node's neighbours inside the node. It doesn't compile, and it can't: in a graph
with a cycle, every node would have to own the others.

Change the representation so edges refer to nodes instead of owning them. Keep the public methods.
