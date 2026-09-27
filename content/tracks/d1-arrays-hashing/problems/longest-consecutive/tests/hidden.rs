use solution::*;

#[test]
fn extremes() {
    check!(r#"nums = [i32::MAX, i32::MIN, i32::MAX - 1]"#, longest_consecutive(&[i32::MAX, i32::MIN, i32::MAX - 1]), 2);
}

#[test]
fn large_run() {
    check!(r#"nums = (0..100000).rev()"#, longest_consecutive(&(0..100_000).rev().collect::<Vec<_>>()), 100000);
}

#[test]
fn single() {
    check!(r#"nums = [7]"#, longest_consecutive(&[7]), 1);
}

#[test]
fn all_same() {
    check!(r#"nums = [7, 7, 7]"#, longest_consecutive(&[7, 7, 7]), 1);
}

#[test]
fn duplicates_inside_run() {
    check!(r#"nums = [1, 2, 2, 3]"#, longest_consecutive(&[1, 2, 2, 3]), 3);
}

#[test]
fn negatives() {
    check!(r#"nums = [-3, -2, -1, 5]"#, longest_consecutive(&[-3, -2, -1, 5]), 3);
}

#[test]
fn crosses_zero() {
    check!(r#"nums = [1, -1, 0]"#, longest_consecutive(&[1, -1, 0]), 3);
}

#[test]
fn two_runs() {
    check!(r#"nums = [10, 11, 1, 2, 3, 12, 13]"#, longest_consecutive(&[10, 11, 1, 2, 3, 12, 13]), 4);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(22);
    for _ in 0..300 {
        let n = rng.below(12);
        let nums: Vec<i32> = rng.vec(n, -8, 8);
        let mut s = nums.clone();
        s.sort();
        s.dedup();
        let (mut best, mut run) = (0, 0);
        for i in 0..s.len() {
            run = if i > 0 && s[i] == s[i - 1] + 1 { run + 1 } else { 1 };
            best = best.max(run);
        }
        check!(format!("nums = {nums:?}"), longest_consecutive(&nums), best);
    }
}

#[test]
fn scale_200k_two_runs() {
    let mut rng = anneal_prelude::Rng::new(23);
    let mut nums: Vec<i32> = (0..120_000).chain(500_000..580_000).collect();
    rng.shuffle(&mut nums);
    check!("nums = 0..120000 and 500000..580000, shuffled", longest_consecutive(&nums), 120_000);
}
