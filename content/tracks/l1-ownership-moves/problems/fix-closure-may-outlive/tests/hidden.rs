use solution::*;

#[test]
fn hundred_calls() {
    check!(r#"start = 0, 100 calls"#, { let mut c = counter(0); (0..100).map(|_| c()).last() }, Some(100));
}
