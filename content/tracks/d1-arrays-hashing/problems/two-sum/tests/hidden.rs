use solution::*;

#[test]
fn negatives() {
    check!(r#"nums = [-3, 4, 3, 90], target = 0"#, two_sum(&[-3, 4, 3, 90], 0), Some((0, 2)));
}

#[test]
fn large_input() {
    check!(r#"nums = 0..10000, target = 19997"#, two_sum(&(0..10_000).collect::<Vec<i32>>(), 19_997), Some((9998, 9999)));
}
