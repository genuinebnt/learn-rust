use solution::*;

#[test]
fn leetcode_valley() {
    check!(r#"ratings = [1, 0, 2]"#, candy(&[1, 0, 2]), 5);
}

#[test]
fn leetcode_equal_neighbours() {
    check!(r#"ratings = [1, 2, 2]"#, candy(&[1, 2, 2]), 4);
}

#[test]
fn nobody() {
    check!(r#"ratings = []"#, candy(&[]), 0);
}

#[test]
fn one_child() {
    check!(r#"ratings = [7]"#, candy(&[7]), 1);
}

#[test]
fn falling() {
    check!(r#"ratings = [3, 2, 1]"#, candy(&[3, 2, 1]), 6);
}

#[test]
fn all_equal() {
    check!(r#"ratings = [2, 2, 2]"#, candy(&[2, 2, 2]), 3);
}
