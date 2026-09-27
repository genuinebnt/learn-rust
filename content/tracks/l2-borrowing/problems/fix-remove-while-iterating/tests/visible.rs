use solution::*;

fn evs(xs: &[(&str, u32)]) -> Vec<Event> {
    xs.iter().map(|&(k, c)| Event { key: k.to_string(), count: c }).collect()
}

fn pairs(v: &[Event]) -> Vec<(&str, u32)> {
    v.iter().map(|e| (e.key.as_str(), e.count)).collect()
}

#[test]
fn example() {
    let mut v = evs(&[("a", 1), ("a", 2), ("b", 5), ("a", 1)]);
    let n = merge_runs(&mut v);
    check!(r#"events [("a", 1), ("a", 2), ("b", 5), ("a", 1)]"#, (n, pairs(&v)), (1, vec![("a", 3), ("b", 5), ("a", 1)]));
}

#[test]
fn empty() {
    let mut v = evs(&[]);
    let n = merge_runs(&mut v);
    check!(r#"events []"#, (n, pairs(&v)), (0, Vec::<(&str, u32)>::new()));
}

#[test]
fn long_run() {
    let mut v = evs(&[("x", 1), ("x", 1), ("x", 1), ("x", 1)]);
    let n = merge_runs(&mut v);
    check!(r#"events [("x", 1), ("x", 1), ("x", 1), ("x", 1)]"#, (n, pairs(&v)), (3, vec![("x", 4)]));
}

#[test]
fn not_adjacent_not_merged() {
    let mut v = evs(&[("a", 1), ("b", 1), ("a", 1)]);
    let n = merge_runs(&mut v);
    check!(r#"events [("a", 1), ("b", 1), ("a", 1)]"#, (n, pairs(&v)), (0, vec![("a", 1), ("b", 1), ("a", 1)]));
}

#[test]
fn two_runs() {
    let mut v = evs(&[("a", 3), ("a", 4), ("b", 1), ("b", 1), ("b", 1)]);
    let n = merge_runs(&mut v);
    check!(r#"events [("a", 3), ("a", 4), ("b", 1), ("b", 1), ("b", 1)]"#, (n, pairs(&v)), (3, vec![("a", 7), ("b", 3)]));
}
