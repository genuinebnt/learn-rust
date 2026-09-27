use solution::*;

#[test]
fn big() {
    check!(r#"data = 0..10000, n = 4"#, sum_everywhere((0..10_000).collect(), 4), vec![49_995_000; 4]);
}
