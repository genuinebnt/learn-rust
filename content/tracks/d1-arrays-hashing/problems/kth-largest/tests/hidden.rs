use solution::*;

#[test]
fn largest() {
    check!(r#"nums = [7, -1], k = 1"#, kth_largest(&mut [7, -1], 1), 7);
}

#[test]
fn smallest() {
    check!(r#"nums = 0..1000, k = 1000"#, kth_largest(&mut (0..1000).collect::<Vec<_>>(), 1000), 0);
}
