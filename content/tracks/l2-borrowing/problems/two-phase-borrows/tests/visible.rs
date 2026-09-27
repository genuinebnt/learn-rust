use solution::*;

#[test]
fn three() {
    check!(r#"v = [], n = 3"#, { let mut v = vec![]; push_lengths(&mut v, 3); v }, vec![0, 1, 2]);
}

#[test]
fn zero_times() {
    check!(r#"v = [4], n = 0"#, { let mut v = vec![4]; push_lengths(&mut v, 0); v }, vec![4]);
}
