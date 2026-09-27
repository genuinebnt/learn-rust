use solution::*;

#[test]
fn empty() {
    check!(r#"v = [], x = -2"#, { let mut v = vec![]; (add_and_max(&mut v, -2), v) }, (-2, vec![-2]));
}
