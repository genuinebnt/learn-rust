`Tree` stores a binary search tree in one `Vec`, with child links as indices. It works, but it will hold
hundreds of millions of nodes, and each `Node` is 20 bytes: `i32` + two `Option<u32>` of 8 bytes each.

Get `Node` down to **12 bytes** without changing what the tree does. The links must stay `Option`s (the tests
call `.is_none()` on them), and the tree must still work past 65 536 nodes. No `unsafe`.
