use solution::*;

#[test]
fn extremes() {
    check!(r#"nums = [i32::MAX, i32::MIN, i32::MAX - 1]"#, longest_consecutive(&[i32::MAX, i32::MIN, i32::MAX - 1]), 2);
}

#[test]
fn large_run() {
    check!(r#"nums = (0..100000).rev()"#, longest_consecutive(&(0..100_000).rev().collect::<Vec<_>>()), 100000);
}
