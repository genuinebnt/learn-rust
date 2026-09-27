use solution::*;

#[test]
fn leetcode_one_way() {
    check!(r#"hats = [[3, 4], [4, 5], [5]]"#, number_ways(&[vec![3, 4], vec![4, 5], vec![5]]), 1);
}

#[test]
fn leetcode_four_ways() {
    check!(r#"hats = [[3, 5, 1], [3, 5]]"#, number_ways(&[vec![3, 5, 1], vec![3, 5]]), 4);
}

#[test]
fn leetcode_all_alike() {
    check!(r#"hats = [[1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4]]"#, number_ways(&[vec![1, 2, 3, 4], vec![1, 2, 3, 4], vec![1, 2, 3, 4], vec![1, 2, 3, 4]]), 24);
}

#[test]
fn nobody() {
    check!(r#"hats = []"#, number_ways(&[]), 1);
}

#[test]
fn same_single_hat() {
    check!(r#"hats = [[5], [5]]"#, number_ways(&[vec![5], vec![5]]), 0);
}
