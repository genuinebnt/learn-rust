//! Port of `src/include/storage/index/int_comparator.h`.

use std::cmp::Ordering;

use super::generic_key::KeyComparator;

/// Compares plain integers. BusTub: `class IntComparator { auto operator()(int lhs, int rhs) const -> int { ... -1, 0, 1 } }`.
#[derive(Clone, Copy, Debug, Default)]
pub struct IntComparator;

impl KeyComparator<i32> for IntComparator {
    fn compare(&self, lhs: &i32, rhs: &i32) -> Ordering {
        todo!("2a-01: the natural order of the integers")
    }
}
