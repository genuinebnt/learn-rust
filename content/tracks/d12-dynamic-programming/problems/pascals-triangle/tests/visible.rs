use solution::*;

#[test]
fn leetcode_five() {
    check!(r#"num_rows = 5"#, generate(5), vec![vec![1], vec![1, 1], vec![1, 2, 1], vec![1, 3, 3, 1], vec![1, 4, 6, 4, 1]]);
}

#[test]
fn leetcode_one() {
    check!(r#"num_rows = 1"#, generate(1), vec![vec![1u64]]);
}

#[test]
fn zero_rows() {
    check!(r#"num_rows = 0"#, generate(0), Vec::<Vec<u64>>::new());
}

#[test]
fn two_rows() {
    check!(r#"num_rows = 2"#, generate(2), vec![vec![1], vec![1, 1]]);
}

#[test]
fn row_six() {
    check!(r#"num_rows = 7, last row"#, generate(7).pop(), Some(vec![1, 6, 15, 20, 15, 6, 1]));
}
