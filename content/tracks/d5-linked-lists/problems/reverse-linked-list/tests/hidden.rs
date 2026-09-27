use solution::*;

#[test]
fn empty() {
    check!(r#"[]"#, reverse(None), None);
}

#[test]
fn long() {
    let v: Vec<i32> = (0..10_000).collect();
    check!(r#"10⁴ nodes"#, values(&reverse(list(&v))) == v.iter().rev().copied().collect::<Vec<_>>(), true);
}
