/// Swaps the elements at `i` and `j`.
pub fn swap_items(v: &mut [String], i: usize, j: usize) {
    let a = &mut v[i];
    let b = &mut v[j];
    let tmp = std::mem::take(a);
    *a = std::mem::take(b);
    *b = tmp;
}
