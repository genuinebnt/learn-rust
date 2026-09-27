use solution::*;

#[test]
fn three_threads() {
    check!(r#"data = [1, 2, 3], n = 3"#, sum_everywhere(vec![1, 2, 3], 3), vec![6, 6, 6]);
}

#[test]
fn no_threads() {
    check!(r#"n = 0"#, sum_everywhere(vec![1], 0), Vec::<u64>::new());
}

#[test]
fn one_thread() {
    check!(r#"data = [4, 5], n = 1"#, sum_everywhere(vec![4, 5], 1), vec![9]);
}

#[test]
fn empty_data_visible() {
    check!(r#"data = [], n = 2"#, sum_everywhere(vec![], 2), vec![0, 0]);
}

#[test]
fn two_threads() {
    check!(r#"data = [10, 20], n = 2"#, sum_everywhere(vec![10, 20], 2), vec![30, 30]);
}
