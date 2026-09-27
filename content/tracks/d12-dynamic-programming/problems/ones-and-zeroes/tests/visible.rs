use solution::*;

#[test]
fn leetcode_five() {
    check!(r#"strs = ["10", "0001", "111001", "1", "0"], m = 5, n = 3"#, find_max_form(&["10", "0001", "111001", "1", "0"], 5, 3), 4);
}

#[test]
fn leetcode_three() {
    check!(r#"strs = ["10", "0", "1"], m = 1, n = 1"#, find_max_form(&["10", "0", "1"], 1, 1), 2);
}

#[test]
fn no_strings() {
    check!(r#"strs = [], m = 5, n = 5"#, find_max_form(&[], 5, 5), 0);
}

#[test]
fn no_budget() {
    check!(r#"strs = ["0"], m = 0, n = 0"#, find_max_form(&["0"], 0, 0), 0);
}

#[test]
fn each_string_once() {
    check!(r#"strs = ["0"], m = 5, n = 5"#, find_max_form(&["0"], 5, 5), 1);
}
