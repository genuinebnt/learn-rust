pub fn dedup_sorted(v: &mut [i32]) -> usize {
    let mut len = v.len();
    let mut i = 1;
    while i < len {
        if v[i] == v[i - 1] {
            for j in i..len - 1 {
                v[j] = v[j + 1];
            }
            len -= 1;
        } else {
            i += 1;
        }
    }
    len
}
