pub fn reverse_in_place(s: &mut [u8]) {
    let (mut l, mut r) = (0, s.len());
    while l + 1 < r {
        r -= 1;
        s.swap(l, r);
        l += 1;
    }
}
