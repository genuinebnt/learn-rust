/// Swaps the elements at `i` and `j`.
pub fn swap_items(v: &mut [String], i: usize, j: usize) {
    if i == j {
        return;
    }
    let (left, right) = v.split_at_mut(j);
    let (a, b) = (&mut left[i], &mut right[0]);
    let tmp = std::mem::take(a);
    *a = std::mem::take(b);
    *b = tmp;
}
