use solution::*;

#[test]
fn leetcode_one() {
    check!(r#"k = 2, w = 0, profits = [1, 2, 3], capital = [0, 1, 1]"#, find_maximized_capital(2, 0, &[1, 2, 3], &[0, 1, 1]), 4);
}

#[test]
fn leetcode_two() {
    check!(r#"k = 3, w = 0, profits = [1, 2, 3], capital = [0, 1, 2]"#, find_maximized_capital(3, 0, &[1, 2, 3], &[0, 1, 2]), 6);
}

#[test]
fn nothing_affordable() {
    check!(r#"k = 3, w = 1, profits = [5, 9], capital = [2, 3]"#, find_maximized_capital(3, 1, &[5, 9], &[2, 3]), 1);
}

#[test]
fn k_zero() {
    check!(r#"k = 0, w = 7, profits = [100], capital = [0]"#, find_maximized_capital(0, 7, &[100], &[0]), 7);
}

#[test]
fn each_project_once() {
    check!(r#"k = 5, w = 0, profits = [4], capital = [0]"#, find_maximized_capital(5, 0, &[4], &[0]), 4);
}

#[test]
fn unlock_the_big_one_first() {
    check!(r#"k = 2, w = 0, profits = [1, 1, 10], capital = [0, 0, 1]"#, find_maximized_capital(2, 0, &[1, 1, 10], &[0, 0, 1]), 11);
}
