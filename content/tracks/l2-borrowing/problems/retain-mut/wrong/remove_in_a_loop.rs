pub fn drop_zeros_and_halve(v: &mut Vec<i32>) {
    let mut i = 0;
    while i < v.len() {
        if v[i] == 0 {
            v.remove(i);
        } else {
            v[i] /= 2;
            i += 1;
        }
    }
}
