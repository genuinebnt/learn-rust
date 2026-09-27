Fill in `Config`. The signatures are written with elided lifetimes; the tests check what they
borrow from. In particular, the result of `tag_with_prefix` must stay usable after `prefix` is gone.
