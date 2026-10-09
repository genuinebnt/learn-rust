//! The random height of a skip-list node, from a source of coin flips.

pub fn random_height(mut flip: impl FnMut() -> bool, max: usize) -> usize {
    let mut level = 1;
    while flip() && level <= max {
        level += 1;
    }
    level
}
