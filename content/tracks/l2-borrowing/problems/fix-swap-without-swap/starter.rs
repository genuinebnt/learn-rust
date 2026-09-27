use std::mem::take;

/// Swaps `v[i]` and `v[j]`. `i` may equal `j`.
pub fn swap_items(v: &mut [String], i: usize, j: usize) {
    let a = &mut v[i];
    let b = &mut v[j];
    let tmp = take(a);
    *a = take(b);
    *b = tmp;
}

/// Rotates three distinct slots: `v[i]` gets `v[j]`'s value, `v[j]` gets `v[k]`'s, `v[k]` gets `v[i]`'s.
pub fn rotate3(v: &mut [String], i: usize, j: usize, k: usize) {
    let (a, b, c) = (&mut v[i], &mut v[j], &mut v[k]);
    let first = take(a);
    *a = take(b);
    *b = take(c);
    *c = first;
}

/// Appends a copy of `v[j]` to `v[i]`. `i` may equal `j` (the string doubles).
pub fn append_copy(v: &mut [String], i: usize, j: usize) {
    v[i].push_str(&v[j]);
}
