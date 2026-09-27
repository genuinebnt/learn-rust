use solution::*;

#[test]
fn leetcode_three_values() {
    check!(r#"nums = [3, 4, 2]"#, delete_and_earn(&[3, 4, 2]), 6);
}

#[test]
fn leetcode_repeats() {
    check!(r#"nums = [2, 2, 3, 3, 3, 4]"#, delete_and_earn(&[2, 2, 3, 3, 3, 4]), 9);
}

#[test]
fn empty() {
    check!(r#"nums = []"#, delete_and_earn(&[]), 0);
}

#[test]
fn single() {
    check!(r#"nums = [5]"#, delete_and_earn(&[5]), 5);
}

#[test]
fn copies_all_count() {
    check!(r#"nums = [1, 1, 1]"#, delete_and_earn(&[1, 1, 1]), 3);
}

#[test]
fn gaps_are_free() {
    check!(r#"nums = [1, 3]"#, delete_and_earn(&[1, 3]), 4);
}
