/// Mutable references to `v[i]` and `v[j]`, in that order. `None` if `i == j` or either is out of bounds.
pub fn pair_mut<T>(v: &mut [T], i: usize, j: usize) -> Option<(&mut T, &mut T)> {
    if i == j || i >= v.len() || j >= v.len() {
        return None;
    }
    let (lo, hi) = (i.min(j), i.max(j));
    let (left, right) = v.split_at_mut(hi);
    let (a, b) = (&mut left[lo], &mut right[0]);
    Some(if i < j { (a, b) } else { (b, a) })
}

/// Calls `f(&mut v[k], &mut v[k + 1])` for every adjacent pair, left to right. Later calls see the changes
/// earlier calls made.
pub fn for_each_adjacent_mut<T>(v: &mut [T], mut f: impl FnMut(&mut T, &mut T)) {
    for k in 1..v.len() {
        let (left, right) = v.split_at_mut(k);
        f(&mut left[k - 1], &mut right[0]);
    }
}
