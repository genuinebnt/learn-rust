use solution::*;

#[test]
fn existing() {
    check!(r#"v = [9], n = 2"#, { let mut v = vec![9]; push_lengths(&mut v, 2); v }, vec![9, 1, 2]);
}
