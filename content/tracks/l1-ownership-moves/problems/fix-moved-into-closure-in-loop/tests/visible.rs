use solution::*;

#[test]
fn three_threads() {
    check!(r#"data = [1, 2, 3], n = 3"#, sum_everywhere(vec![1, 2, 3], 3), vec![6, 6, 6]);
}

#[test]
fn no_threads() {
    check!(r#"n = 0"#, sum_everywhere(vec![1], 0), Vec::<u64>::new());
}
