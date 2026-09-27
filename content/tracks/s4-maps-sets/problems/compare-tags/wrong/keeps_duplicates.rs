use std::collections::HashSet;

pub fn compare_tags(a: &[&str], b: &[&str]) -> (Vec<String>, Vec<String>, Vec<String>) {
    let sa: HashSet<&str> = a.iter().copied().collect();
    let sb: HashSet<&str> = b.iter().copied().collect();
    let pick = |from: &[&str], other: &HashSet<&str>, want: bool| {
        let mut v: Vec<String> = from.iter().filter(|t| other.contains(*t) == want).map(|t| t.to_string()).collect();
        v.sort();
        v
    };
    (pick(a, &sb, true), pick(a, &sb, false), pick(b, &sa, false))
}
