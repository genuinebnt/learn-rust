pub fn clean(v: &mut Vec<i32>) {
    v.retain(|&x| x >= 0);
    v.dedup();
}
