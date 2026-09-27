use solution::*;

#[test]
fn leetcode_example() {
    let mut m = MedianFinder::new();
    m.add_num(1);
    m.add_num(2);
    let a = m.find_median();
    m.add_num(3);
    check!(r#"add 1, add 2, find_median, add 3, find_median"#, (a, m.find_median()), (Some(1.5), Some(2.0)));
}

#[test]
fn empty() {
    check!(r#"new, find_median"#, MedianFinder::new().find_median(), None);
}

#[test]
fn remove_the_middle() {
    let mut m = MedianFinder::new();
    m.add_num(1);
    m.add_num(2);
    m.add_num(3);
    let removed = m.remove_num(2);
    check!(r#"add 1, add 2, add 3, remove 2 → [1, 3]"#, (removed, m.find_median()), (true, Some(2.0)));
}

#[test]
fn remove_missing_value() {
    let mut m = MedianFinder::new();
    m.add_num(5);
    check!(r#"add 5, remove 7"#, (m.remove_num(7), m.find_median()), (false, Some(5.0)));
}

#[test]
fn duplicates_are_copies() {
    let mut m = MedianFinder::new();
    m.add_num(4);
    m.add_num(4);
    m.add_num(9);
    check!(r#"add 4, add 4, add 9, remove 4 → [4, 9]"#, (m.remove_num(4), m.find_median()), (true, Some(6.5)));
}

#[test]
fn large_values_average() {
    let mut m = MedianFinder::new();
    m.add_num(i32::MAX);
    m.add_num(i32::MAX - 2);
    check!(r#"add i32::MAX, add i32::MAX - 2"#, m.find_median(), Some(2147483646.0));
}
