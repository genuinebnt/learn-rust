pub fn drop_zeros_and_halve(v: &mut Vec<i32>) {
    v.retain_mut(|x| {
        *x /= 2;
        *x != 0
    });
}
