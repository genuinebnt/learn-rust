pub fn reverse_in_place(s: &mut [u8]) {
    let n = s.len();
    if n == 0 {
        return;
    }
    for i in 0..(n - 1) / 2 {
        s.swap(i, n - 1 - i);
    }
}
