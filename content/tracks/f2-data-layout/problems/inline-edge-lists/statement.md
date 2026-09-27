A compiler's control-flow graph keeps each block's successors and predecessors. Nearly every block has at
most 4 edges each way (a `goto`, an `if`, a small `match`); a big `switch` is rare. With a `Vec` per
list, building the CFG of a large function allocates twice per block.

1. Change the edge lists so that `size_of::<Block>()` stays **at most 56 bytes**, and building a graph
   where no block has more than **4** edges each way makes **no allocation** once `Cfg::with_capacity`
   has reserved the blocks. Larger switches must still work. (`smallvec` is available.)
2. Write `split_critical_edges`: every edge from a block with several successors to a block with
   several predecessors gets a new empty block (0 statements) on it, which takes the edge's place in
   both lists. Visit blocks in id order (only the original ones) and successors in order, so new ids
   come out in that order; return how many edges were split.

`add_edge`, the accessors and `reverse_postorder` keep their behaviour.
