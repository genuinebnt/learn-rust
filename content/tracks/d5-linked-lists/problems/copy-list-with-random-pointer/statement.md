Each node has `next` and a `random` pointer to any node (or none). Copy the list into an arena:
`Vec<(value, random index)>` in list order, where the random index is the position of the node it points to.
