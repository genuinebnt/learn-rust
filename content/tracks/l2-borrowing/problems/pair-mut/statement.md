Write `pair_mut`, which returns `&mut` to two different elements at once, and `for_each_adjacent_mut`,
which hands a closure each adjacent pair mutably: the `windows_mut` that std doesn't have. No `unsafe`,
and no `get_disjoint_mut` (write the split yourself).
