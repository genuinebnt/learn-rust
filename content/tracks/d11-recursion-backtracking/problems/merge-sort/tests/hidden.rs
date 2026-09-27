use solution::*;

#[test]
fn two_swapped() {
    check!(r#"nums = [2, 1]"#, merge_sort(&[2, 1]), vec![1, 2]);
}

#[test]
fn reversed() {
    check!(r#"nums = [9, 8, …, 0]"#, merge_sort(&(0..10).rev().collect::<Vec<i32>>()), (0..10).collect::<Vec<i32>>());
}

#[test]
fn all_equal() {
    check!(r#"nums = [4, 4, 4, 4, 4]"#, merge_sort(&[4, 4, 4, 4, 4]), vec![4, 4, 4, 4, 4]);
}

#[test]
fn extremes() {
    check!(r#"nums = [i32::MAX, 0, i32::MIN, -1]"#, merge_sort(&[i32::MAX, 0, i32::MIN, -1]), vec![i32::MIN, -1, 0, i32::MAX]);
}

#[test]
fn odd_length() {
    check!(r#"nums = [3, 1, 2]"#, merge_sort(&[3, 1, 2]), vec![1, 2, 3]);
}

#[test]
fn tail_left_over() {
    check!(r#"nums = [1, 2, 3, 10, 11, 12, 4]"#, merge_sort(&[1, 2, 3, 10, 11, 12, 4]), vec![1, 2, 3, 4, 10, 11, 12]);
}

#[test]
fn negatives_only() {
    check!(r#"nums = [-3, -1, -2]"#, merge_sort(&[-3, -1, -2]), vec![-3, -2, -1]);
}

#[test]
fn single_negative() {
    check!(r#"nums = [-5]"#, merge_sort(&[-5]), vec![-5]);
}

#[test]
fn random_vs_std_sort() {
    let mut rng = anneal_prelude::Rng::new(1105);
    for _ in 0..300 {
        let n = rng.below(30);
        let nums: Vec<i32> = rng.vec(n, -20, 20);
        let mut want = nums.clone();
        want.sort();
        check!(format!("nums = {nums:?}"), merge_sort(&nums), want);
    }
}

#[test]
fn scale_200k_reversed() {
    let nums: Vec<i32> = (0..200_000).rev().collect();
    let out = merge_sort(&nums);
    check!("nums = [199999, 199998, …, 0]", out == (0..200_000).collect::<Vec<i32>>(), true);
}

#[test]
fn scale_200k_random() {
    let mut rng = anneal_prelude::Rng::new(1106);
    let nums: Vec<i32> = rng.vec(200_000, i32::MIN as i64, i32::MAX as i64);
    let mut want = nums.clone();
    want.sort();
    check!("nums = 200000 random values", merge_sort(&nums) == want, true);
}
