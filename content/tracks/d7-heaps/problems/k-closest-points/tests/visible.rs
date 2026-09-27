use solution::*;

#[test]
fn leetcode_one() {
    check!(r#"points = [(1, 3), (-2, 2)], k = 1"#, k_closest(&[(1, 3), (-2, 2)], 1), vec![(-2, 2)]);
}

#[test]
fn leetcode_two() {
    check!(r#"points = [(3, 3), (5, -1), (-2, 4)], k = 2"#, k_closest(&[(3, 3), (5, -1), (-2, 4)], 2), vec![(3, 3), (-2, 4)]);
}

#[test]
fn ties_in_x_then_y_order() {
    check!(r#"points = [(1, 0), (0, 1), (-1, 0), (0, -1)], k = 3"#, k_closest(&[(1, 0), (0, 1), (-1, 0), (0, -1)], 3), vec![(-1, 0), (0, -1), (0, 1)]);
}

#[test]
fn k_zero() {
    check!(r#"points = [(1, 1)], k = 0"#, k_closest(&[(1, 1)], 0), Vec::<(i32, i32)>::new());
}

#[test]
fn k_past_the_end() {
    check!(r#"points = [(2, 2), (1, 1)], k = 5"#, k_closest(&[(2, 2), (1, 1)], 5), vec![(1, 1), (2, 2)]);
}

#[test]
fn repeated_point_counts_twice() {
    check!(r#"points = [(2, 0), (1, 1), (1, 1)], k = 2"#, k_closest(&[(2, 0), (1, 1), (1, 1)], 2), vec![(1, 1), (1, 1)]);
}
