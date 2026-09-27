/// Removes every name starting with `prefix`.
pub fn remove_prefixed(names: &mut Vec<String>, prefix: &str) {
    names.retain(|n| !n.starts_with(prefix));
}
