use solution::*;

#[test]
fn leetcode_one_fits() {
    check!(r#"greed = [1, 2, 3], cookies = [1, 1]"#, find_content_children(&[1, 2, 3], &[1, 1]), 1);
}

#[test]
fn leetcode_all_fit() {
    check!(r#"greed = [1, 2], cookies = [1, 2, 3]"#, find_content_children(&[1, 2], &[1, 2, 3]), 2);
}

#[test]
fn no_cookies() {
    check!(r#"greed = [1, 2], cookies = []"#, find_content_children(&[1, 2], &[]), 0);
}

#[test]
fn no_children() {
    check!(r#"greed = [], cookies = [4]"#, find_content_children(&[], &[4]), 0);
}

#[test]
fn equal_size_is_enough() {
    check!(r#"greed = [5], cookies = [5]"#, find_content_children(&[5], &[5]), 1);
}

#[test]
fn one_cookie_per_child() {
    check!(r#"greed = [1], cookies = [1, 1, 1]"#, find_content_children(&[1], &[1, 1, 1]), 1);
}

#[test]
fn inputs_unsorted() {
    check!(r#"greed = [3, 1, 2], cookies = [3, 1]"#, find_content_children(&[3, 1, 2], &[3, 1]), 2);
}
