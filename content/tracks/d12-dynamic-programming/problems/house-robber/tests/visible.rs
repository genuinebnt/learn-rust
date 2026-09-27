use solution::*;

#[test]
fn leetcode_four() {
    check!(r#"nums = [1, 2, 3, 1]"#, rob(&[1, 2, 3, 1]), 4);
}

#[test]
fn leetcode_five() {
    check!(r#"nums = [2, 7, 9, 3, 1]"#, rob(&[2, 7, 9, 3, 1]), 12);
}

#[test]
fn empty() {
    check!(r#"nums = []"#, rob(&[]), 0);
}

#[test]
fn single() {
    check!(r#"nums = [5]"#, rob(&[5]), 5);
}

#[test]
fn not_every_other_house() {
    check!(r#"nums = [2, 1, 1, 2]"#, rob(&[2, 1, 1, 2]), 4);
}
