use solution::*;

fn norm<T: Ord>(mut groups: Vec<Vec<T>>) -> Vec<Vec<T>> {
    for g in &mut groups {
        g.sort();
    }
    groups.sort();
    groups
}

#[test]
fn leetcode_three_seven() {
    check!(r#"k = 3, n = 7"#, norm(combination_sum3(3, 7)), vec![vec![1, 2, 4]]);
}

#[test]
fn leetcode_three_nine() {
    check!(r#"k = 3, n = 9"#, norm(combination_sum3(3, 9)), vec![vec![1, 2, 6], vec![1, 3, 5], vec![2, 3, 4]]);
}

#[test]
fn leetcode_none() {
    check!(r#"k = 4, n = 1"#, combination_sum3(4, 1), Vec::<Vec<u32>>::new());
}

#[test]
fn one_digit() {
    check!(r#"k = 1, n = 5"#, combination_sum3(1, 5), vec![vec![5]]);
}

#[test]
fn digits_stop_at_nine() {
    check!(r#"k = 1, n = 10"#, combination_sum3(1, 10), Vec::<Vec<u32>>::new());
}
