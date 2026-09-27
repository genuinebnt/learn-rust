/// Removes the elements at `indices` (any order, repeats allowed, out-of-range ones ignored), keeping the
/// rest in order. O(n + k log k).
pub fn remove_indices<T>(v: &mut Vec<T>, indices: &[usize]) {
    let mut idx = indices.to_vec();
    idx.sort_unstable();
    idx.dedup();
    for i in idx {
        if i < v.len() {
            v.remove(i);
        }
    }
}

/// Removes the elements at `indices` with `swap_remove`, highest index first, and returns them in that
/// order. The order of what's left is whatever that produces. O(k log k): nothing is shifted.
pub fn remove_indices_unordered<T>(v: &mut Vec<T>, indices: &[usize]) -> Vec<T> {
    let mut idx: Vec<usize> = indices.iter().copied().filter(|&i| i < v.len()).collect();
    idx.sort_unstable_by(|a, b| b.cmp(a));
    idx.dedup();
    idx.into_iter().map(|i| v.swap_remove(i)).collect()
}
