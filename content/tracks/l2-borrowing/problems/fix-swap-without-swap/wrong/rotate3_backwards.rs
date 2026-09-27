use std::mem::take;

/// Swaps `v[i]` and `v[j]`. `i` may equal `j`.
pub fn swap_items(v: &mut [String], i: usize, j: usize) {
    if i == j {
        return;
    }
    let tmp = take(&mut v[i]);
    v[i] = std::mem::replace(&mut v[j], tmp);
}

/// Rotates three distinct slots: `v[i]` gets `v[j]`'s value, `v[j]` gets `v[k]`'s, `v[k]` gets `v[i]`'s.
pub fn rotate3(v: &mut [String], i: usize, j: usize, k: usize) {
    let first = take(&mut v[k]);
    v[k] = take(&mut v[j]);
    v[j] = take(&mut v[i]);
    v[i] = first;
}

/// Appends a copy of `v[j]` to `v[i]`. `i` may equal `j` (the string doubles).
pub fn append_copy(v: &mut [String], i: usize, j: usize) {
    if i == j {
        v[i].extend_from_within(..);
        return;
    }
    let (lo, hi) = (i.min(j), i.max(j));
    let (left, right) = v.split_at_mut(hi);
    let (a, b) = (&mut left[lo], &mut right[0]);
    if i < j {
        a.push_str(b);
    } else {
        b.push_str(a);
    }
}
