pub fn reverse_in_place(s: &mut [u8]) {
    let n = s.len();
    for i in 0..n {
        s.swap(i, n - 1 - i);
    }
}
