use solution::*;

#[test]
fn leetcode_true() {
    check!(r#"nums = [1, 5, 11, 5]"#, can_partition(&[1, 5, 11, 5]), true);
}

#[test]
fn leetcode_false() {
    check!(r#"nums = [1, 2, 3, 5]"#, can_partition(&[1, 2, 3, 5]), false);
}

#[test]
fn empty() {
    check!(r#"nums = []"#, can_partition(&[]), true);
}

#[test]
fn single() {
    check!(r#"nums = [1]"#, can_partition(&[1]), false);
}

#[test]
fn pair() {
    check!(r#"nums = [1, 1]"#, can_partition(&[1, 1]), true);
}

#[test]
fn even_total_is_not_enough() {
    check!(r#"nums = [1, 2, 5]"#, can_partition(&[1, 2, 5]), false);
}
