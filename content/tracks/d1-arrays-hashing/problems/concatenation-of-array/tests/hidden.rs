use solution::*;

#[test]
fn one() {
    check!(r#"nums = [7]"#, concat_twice(&[7]), vec![7, 7]);
}

#[test]
fn length() {
    check!(r#"nums = 0..1000"#, concat_twice(&(0..1000).collect::<Vec<_>>()).len(), 2000);
}
