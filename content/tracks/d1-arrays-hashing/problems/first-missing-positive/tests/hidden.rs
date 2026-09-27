use solution::*;

#[test]
fn duplicates() {
    check!(r#"nums = [1, 1]"#, first_missing_positive(&mut [1, 1]), 2);
}

#[test]
fn empty() {
    check!(r#"nums = []"#, first_missing_positive(&mut []), 1);
}

#[test]
fn permutation() {
    check!(r#"nums = (1..=1000).rev()"#, first_missing_positive(&mut (1..=1000).rev().collect::<Vec<_>>()), 1001);
}

#[test]
fn single_one() {
    check!(r#"nums = [1]"#, first_missing_positive(&mut [1]), 2);
}

#[test]
fn single_two() {
    check!(r#"nums = [2]"#, first_missing_positive(&mut [2]), 1);
}

#[test]
fn only_non_positive() {
    check!(r#"nums = [0, -1, -5]"#, first_missing_positive(&mut [0, -1, -5]), 1);
}

#[test]
fn extremes() {
    check!(r#"nums = [i32::MAX, i32::MIN, 1]"#, first_missing_positive(&mut [i32::MAX, i32::MIN, 1]), 2);
}

#[test]
fn repeated_out_of_place() {
    check!(r#"nums = [2, 2, 2]"#, first_missing_positive(&mut [2, 2, 2]), 1);
}

#[test]
fn pairs() {
    check!(r#"nums = [1, 1, 2, 2]"#, first_missing_positive(&mut [1, 1, 2, 2]), 3);
}

#[test]
fn value_equals_len() {
    check!(r#"nums = [3, 1, 2]"#, first_missing_positive(&mut [3, 1, 2]), 4);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(25);
    for _ in 0..300 {
        let n = rng.below(10);
        let nums: Vec<i32> = rng.vec(n, -3, 11);
        let want = (1..).find(|x| !nums.contains(x)).unwrap();
        check!(format!("nums = {nums:?}"), first_missing_positive(&mut nums.clone()), want);
    }
}

#[test]
fn scale_200k() {
    let mut rng = anneal_prelude::Rng::new(26);
    let mut nums: Vec<i32> = (1..=200_000).filter(|&x| x != 123_457).collect();
    nums.push(-4);
    rng.shuffle(&mut nums);
    check!("nums = 1..=200000 without 123457, plus -4, shuffled", first_missing_positive(&mut nums), 123_457);
}
