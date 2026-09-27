use solution::*;

#[test]
fn zero() {
    check!(r#"take 0 from empty"#, Reader::new(&[]).take(0), Some(&[][..]));
}
