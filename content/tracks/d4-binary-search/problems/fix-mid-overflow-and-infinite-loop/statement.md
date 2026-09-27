`last_true` finds the largest `x` in `lo..=hi` for which `pred(x)` is true (pred is true up to some
point, then false). It has two bugs: one panics near `u32::MAX`, and one loops forever on a range of
two values. Fix both by changing one line.
