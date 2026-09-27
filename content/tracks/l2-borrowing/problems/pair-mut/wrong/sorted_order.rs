pub fn pair_mut<T>(v: &mut [T], i: usize, j: usize) -> Option<(&mut T, &mut T)> {
    if i == j || i >= v.len() || j >= v.len() {
        return None;
    }
    let (lo, hi) = (i.min(j), i.max(j));
    let (left, right) = v.split_at_mut(hi);
    let (a, b) = (&mut left[lo], &mut right[0]);
    Some((a, b))
}
