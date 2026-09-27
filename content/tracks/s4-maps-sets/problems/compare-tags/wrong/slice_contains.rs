pub fn compare_tags(a: &[&str], b: &[&str]) -> (Vec<String>, Vec<String>, Vec<String>) {
    let pick = |from: &[&str], other: &[&str], want: bool| {
        let mut v: Vec<String> = from.iter().filter(|t| other.contains(t) == want).map(|t| t.to_string()).collect();
        v.sort();
        v.dedup();
        v
    };
    (pick(a, b, true), pick(a, b, false), pick(b, a, false))
}
