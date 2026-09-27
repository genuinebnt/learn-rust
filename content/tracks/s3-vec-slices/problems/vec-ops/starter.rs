/// Removes the elements at `indices` (any order, repeats allowed, out-of-range ones ignored), keeping the
/// rest in order. O(n + k log k).
pub fn remove_indices<T>(v: &mut Vec<T>, indices: &[usize]) {
    todo!()
}

/// Removes the elements at `indices` with `swap_remove`, highest index first, and returns them in that
/// order. The order of what's left is whatever that produces. O(k log k): nothing is shifted.
pub fn remove_indices_unordered<T>(v: &mut Vec<T>, indices: &[usize]) -> Vec<T> {
    todo!()
}
