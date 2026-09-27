use solution::*;

#[test]
fn many() {
    check!(r#"8 chunks of 0..1000"#, parallel_sum((0..8).map(|_| (0..1000).collect()).collect()), 8 * 499_500);
}
