use solution::*;

#[test]
fn leetcode_three() {
    check!(r#"nums = [2, 3, 2]"#, rob(&[2, 3, 2]), 3);
}

#[test]
fn leetcode_four() {
    check!(r#"nums = [1, 2, 3, 1]"#, rob(&[1, 2, 3, 1]), 4);
}

#[test]
fn leetcode_one_two_three() {
    check!(r#"nums = [1, 2, 3]"#, rob(&[1, 2, 3]), 3);
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
fn ends_are_neighbours() {
    check!(r#"nums = [5, 1, 1, 5]"#, rob(&[5, 1, 1, 5]), 6);
}
