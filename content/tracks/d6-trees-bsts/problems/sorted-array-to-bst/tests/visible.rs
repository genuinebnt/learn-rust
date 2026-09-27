use solution::*;

#[test]
fn leetcode_example() {
    check!(r#"nums = [-10,-3,0,5,9]"#, level_order_values(&sorted_array_to_bst(&[-10, -3, 0, 5, 9])), vec![Some(0), Some(-3), Some(9), Some(-10), None, Some(5)]);
}

#[test]
fn leetcode_two() {
    check!(r#"nums = [1,3]"#, level_order_values(&sorted_array_to_bst(&[1, 3])), vec![Some(3), Some(1)]);
}

#[test]
fn empty() {
    check!(r#"nums = []"#, sorted_array_to_bst(&[]), None);
}

#[test]
fn single() {
    check!(r#"nums = [7]"#, level_order_values(&sorted_array_to_bst(&[7])), vec![Some(7)]);
}

#[test]
fn three() {
    check!(r#"nums = [1,2,3]"#, level_order_values(&sorted_array_to_bst(&[1, 2, 3])), vec![Some(2), Some(1), Some(3)]);
}
