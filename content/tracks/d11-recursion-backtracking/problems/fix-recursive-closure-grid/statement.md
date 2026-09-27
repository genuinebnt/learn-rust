`island_sizes` should return the size of every island (1s joined up, down, left or right) in the order each
island's first cell appears reading row by row. The flood fill that sinks an island was written as a closure so it
could see `grid` without taking it as a parameter. It doesn't compile.

Rewrite `sink_island` as an inner `fn` that takes the grid as an explicit `&mut` parameter. Keep the recursion.
