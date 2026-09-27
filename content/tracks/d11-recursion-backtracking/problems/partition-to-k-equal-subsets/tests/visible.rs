use solution::*;

#[test]
fn leetcode_four_groups() {
    check!(r#"nums = [4, 3, 2, 3, 5, 2, 1], k = 4"#, can_partition_k_subsets(&[4, 3, 2, 3, 5, 2, 1], 4), true);
}

#[test]
fn leetcode_no_split() {
    check!(r#"nums = [1, 2, 3, 4], k = 3"#, can_partition_k_subsets(&[1, 2, 3, 4], 3), false);
}

#[test]
fn one_group() {
    check!(r#"nums = [5, 1], k = 1"#, can_partition_k_subsets(&[5, 1], 1), true);
}

#[test]
fn each_its_own_group() {
    check!(r#"nums = [2, 2, 2, 2], k = 4"#, can_partition_k_subsets(&[2, 2, 2, 2], 4), true);
}

#[test]
fn number_bigger_than_a_group() {
    check!(r#"nums = [10, 1, 1], k = 2 (each group would sum to 6)"#, can_partition_k_subsets(&[10, 1, 1], 2), false);
}

#[test]
fn sum_divides_but_no_split() {
    check!(r#"nums = [1, 5, 5, 5], k = 2 (groups of 8)"#, can_partition_k_subsets(&[1, 5, 5, 5], 2), false);
}
