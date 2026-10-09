//! Bulk loading a B+ tree: when all the keys are known in advance and sorted, the tree can be built bottom-up in one pass, with leaves as full
//! as the rules allow, instead of by `n` single inserts and the splits they cause. This is the planning half: how many keys go in each leaf.

/// Splits `n` sorted keys into leaves of at most `max` keys. Every leaf except possibly the only one must hold at least `min` keys, where
/// `min = max / 2` (rounded down) and `max >= 2`. Returns each leaf's size, left to right. The leaves are **as few as possible**, and as full as
/// possible from the left; when the last leaf would be too small, the last two leaves share their keys as evenly as possible (the second to last
/// gets the extra one). `n == 0` has no leaves.
pub fn leaf_sizes(n: usize, max: usize) -> Vec<usize> {
    todo!("2c-c1: as few leaves as possible, full from the left, the last two evened out if the last is too small")
}

/// The number of nodes at each level of the tree built over `n` keys, from the leaves up to the root (the last entry is 1). An inner node holds
/// at most `fanout` children and the same rule applies to the children counts as to leaves (`min = fanout / 2`, evened out at the right end).
/// `n == 0` has no levels.
pub fn level_widths(n: usize, leaf_max: usize, fanout: usize) -> Vec<usize> {
    todo!("2c-c1: the number of leaves, then the number of parents of that many nodes, up to a single root")
}
