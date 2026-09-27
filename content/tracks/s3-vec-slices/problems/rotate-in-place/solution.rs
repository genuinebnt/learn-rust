/// Rotates `v` right by `k` with three reversals (no `rotate_*`).
pub fn rotate_right(v: &mut [i32], k: usize) {
    if v.is_empty() {
        return;
    }
    let k = k % v.len();
    v.reverse();
    v[..k].reverse();
    v[k..].reverse();
}

/// Moves the element at `from` to index `to`, shifting everything in between by one place (drag and drop).
/// Does nothing if either index is out of range. Touches only the elements between the two indices.
pub fn move_item<T>(v: &mut [T], from: usize, to: usize) {
    if from >= v.len() || to >= v.len() {
        return;
    }
    if from < to {
        v[from..=to].rotate_left(1);
    } else {
        v[to..=from].rotate_right(1);
    }
}

/// Swaps each pair of neighbours: [1, 2, 3, 4, 5] → [2, 1, 4, 3, 5]. An odd last element stays put.
pub fn swap_pairs<T>(v: &mut [T]) {
    for pair in v.chunks_exact_mut(2) {
        pair.swap(0, 1);
    }
}
