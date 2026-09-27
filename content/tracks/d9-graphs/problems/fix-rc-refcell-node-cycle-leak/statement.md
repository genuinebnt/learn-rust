A tree where each child points back at its parent. It works, but dropping the tree frees nothing,
because parent and child keep each other alive. Fix it so dropping the last outside handle frees
the tree. Keep the public methods.
