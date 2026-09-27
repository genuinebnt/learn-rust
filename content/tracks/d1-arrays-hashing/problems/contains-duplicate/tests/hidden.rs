use solution::*;

#[test]
fn many_repeats() {
    check!(r#"nums = [1, 1, 1, 3, 3, 4, 3, 2, 4, 2]"#, contains_duplicate(&[1, 1, 1, 3, 3, 4, 3, 2, 4, 2]), true);
}

#[test]
fn large_distinct() {
    check!(r#"nums = 0..100000"#, contains_duplicate(&(0..100_000).collect::<Vec<_>>()), false);
}
