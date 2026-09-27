use solution::*;

#[test]
fn mixed() {
    check!(r#"nums = [2, 0, 2, 1, 1, 0]"#, { let mut v = vec![2, 0, 2, 1, 1, 0]; sort_colors(&mut v); v }, vec![0, 0, 1, 1, 2, 2]);
}

#[test]
fn three() {
    check!(r#"nums = [2, 0, 1]"#, { let mut v = vec![2, 0, 1]; sort_colors(&mut v); v }, vec![0, 1, 2]);
}

#[test]
fn single() {
    check!(r#"nums = [0]"#, { let mut v = vec![0]; sort_colors(&mut v); v }, vec![0]);
}
