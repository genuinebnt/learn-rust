`node_for` walks down a trie, creating missing children, and returns the node where `word` ends.
It doesn't compile: the early `return` in the `if let` keeps `node.children[..]` borrowed for the rest of the
function, so the insert below it is rejected (E0506, E0499).

Make it compile without changing what it does. The rest of the file is correct.
