use std::collections::HashSet;

pub fn compare_tags(a: &[&str], b: &[&str]) -> (Vec<String>, Vec<String>, Vec<String>) {
    let a: HashSet<&str> = a.iter().copied().collect();
    let b: HashSet<&str> = b.iter().copied().collect();
    (
        a.intersection(&b).map(|s| s.to_string()).collect(),
        a.difference(&b).map(|s| s.to_string()).collect(),
        b.difference(&a).map(|s| s.to_string()).collect(),
    )
}
