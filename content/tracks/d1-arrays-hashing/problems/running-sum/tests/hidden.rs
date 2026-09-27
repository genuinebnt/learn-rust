use solution::*;

#[test]
fn negatives() {
    check!(r#"nums = [3, -1, -2]"#, running_sum(&[3, -1, -2]), vec![3, 2, 0]);
}

#[test]
fn ten_thousand_ones() {
    check!(r#"nums = [1; 10000]"#, *running_sum(&[1; 10000]).last().unwrap(), 10000);
}

#[test]
fn all_negative() {
    check!(r#"nums = [-1, -2, -3]"#, running_sum(&[-1, -2, -3]), vec![-1, -3, -6]);
}

#[test]
fn zeros() {
    check!(r#"nums = [0, 0, 0]"#, running_sum(&[0, 0, 0]), vec![0, 0, 0]);
}

#[test]
fn single_negative() {
    check!(r#"nums = [-7]"#, running_sum(&[-7]), vec![-7]);
}

#[test]
fn cancels_out() {
    check!(r#"nums = [5, -5, 5, -5]"#, running_sum(&[5, -5, 5, -5]), vec![5, 0, 5, 0]);
}

#[test]
fn past_i16() {
    check!(r#"nums = [10000; 10]"#, running_sum(&[10_000; 10]), (1..=10).map(|i| i * 10_000).collect::<Vec<i32>>());
}

#[test]
fn min_values() {
    check!(r#"nums = [-10000; 200000]"#, *running_sum(&vec![-10_000; 200_000]).last().unwrap(), -2_000_000_000);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1);
    for _ in 0..300 {
        let n = rng.below(20);
        let nums: Vec<i32> = rng.vec(n, -10_000, 10_000);
        let want: Vec<i32> = (0..n).map(|i| nums[..=i].iter().sum()).collect();
        check!(format!("nums = {nums:?}"), running_sum(&nums), want);
    }
}

#[test]
fn scale_200k() {
    let nums: Vec<i32> = (0..200_000).map(|i| if i % 2 == 0 { 10_000 } else { -9_999 }).collect();
    let out = running_sum(&nums);
    check!("nums = [10000, -9999, …] (200000 values)", (out.len(), out[199_998], out[199_999]), (200_000, 109_999, 100_000));
}
