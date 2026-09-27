pub fn clean(v: &mut Vec<i32>) {
    v.dedup();
    v.retain(|&x| x >= 0);
}
