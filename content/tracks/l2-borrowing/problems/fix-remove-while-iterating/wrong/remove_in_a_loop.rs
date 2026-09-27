/// Removes every name starting with `prefix`.
pub fn remove_prefixed(names: &mut Vec<String>, prefix: &str) {
    let mut i = 0;
    while i < names.len() {
        if names[i].starts_with(prefix) {
            names.remove(i);
        } else {
            i += 1;
        }
    }
}
