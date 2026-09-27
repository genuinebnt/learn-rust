pub fn drop_zeros_and_halve(v: &mut Vec<i32>) {
    v.retain_mut(|x| {
        if *x == 0 {
            return false;
        }
        *x >>= 1;
        true
    });
}
