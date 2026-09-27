use solution::*;

#[test]
fn single_both_ways() {
    let mut d = Deque::new();
    check!(r#"push 7; pop_back; then push 8; pop_front"#, { d.push_back(7); let a = d.pop_back(); d.push_front(8); (a, d.pop_front(), d.is_empty()) }, (Some(7), Some(8), true));
}

#[test]
fn drain_from_back() {
    let mut d = Deque::new();
    for i in 0..5 {
        d.push_back(i);
    }
    let out: Vec<i32> = std::iter::from_fn(|| d.pop_back()).collect();
    check!(r#"push_back 0..5; pop_back until empty"#, out, vec![4, 3, 2, 1, 0]);
}

#[test]
fn big_drop() {
    let mut d = Deque::new();
    for i in 0..1_000_000 {
        d.push_back(i);
    }
    check!(r#"push 10⁶ then drop"#, d.len(), 1_000_000);
}
