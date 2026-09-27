pub fn clean(v: &mut Vec<i32>) {
    let mut seen = std::collections::HashSet::new();
    v.retain(|&x| x >= 0 && seen.insert(x));
}
