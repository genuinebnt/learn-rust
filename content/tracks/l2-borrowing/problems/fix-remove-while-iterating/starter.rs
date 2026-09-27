/// Removes every name starting with `prefix`.
pub fn remove_prefixed(names: &mut Vec<String>, prefix: &str) {
    for (i, n) in names.iter().enumerate() {
        if n.starts_with(prefix) {
            names.remove(i);
        }
    }
}
