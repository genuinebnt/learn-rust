/// Swaps the elements at `i` and `j`.
pub fn swap_items(v: &mut [String], i: usize, j: usize) {
    let (lo, hi) = (i.min(j), i.max(j));
    let (left, right) = v.split_at_mut(hi);
    let (a, b) = (&mut left[lo], &mut right[0]);
    let tmp = std::mem::take(a);
    *a = std::mem::take(b);
    *b = tmp;
}
