use solution::*;

#[test]
fn many_dups() {
    check!(r#"nums = [-2, 0, 0, 2, 2, -2]"#, three_sum(&[-2, 0, 0, 2, 2, -2]), vec![[-2, 0, 2]]);
}

#[test]
fn wide() {
    check!(r#"nums = [-4, -1, -1, 0, 1, 2, 3]"#, three_sum(&[-4, -1, -1, 0, 1, 2, 3]), vec![[-4, 1, 3], [-1, -1, 2], [-1, 0, 1]]);
}

#[test]
fn empty() {
    check!(r#"nums = []"#, three_sum(&[]), Vec::<[i32; 3]>::new());
}

#[test]
fn two_values() {
    check!(r#"nums = [0, 0]"#, three_sum(&[0, 0]), Vec::<[i32; 3]>::new());
}

#[test]
fn exactly_three() {
    check!(r#"nums = [3, -1, -2]"#, three_sum(&[3, -1, -2]), vec![[-2, -1, 3]]);
}

#[test]
fn all_positive() {
    check!(r#"nums = [1, 2, 3, 4]"#, three_sum(&[1, 2, 3, 4]), Vec::<[i32; 3]>::new());
}

#[test]
fn many_zeros() {
    check!(r#"nums = [0; 1000]"#, three_sum(&vec![0; 1000]), vec![[0, 0, 0]]);
}

#[test]
fn extremes_no_overflow() {
    check!(r#"nums = [i32::MIN, -1, 1, i32::MAX]"#, three_sum(&[i32::MIN, -1, 1, i32::MAX]), vec![[i32::MIN, 1, i32::MAX]]);
}

#[test]
fn repeated_last() {
    check!(r#"nums = [-2, 1, 1, 1, 1]"#, three_sum(&[-2, 1, 1, 1, 1]), vec![[-2, 1, 1]]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(207);
    for _ in 0..300 {
        let n = rng.below(10);
        let nums: Vec<i32> = rng.vec(n, -6, 6);
        let mut want = std::collections::BTreeSet::new();
        for i in 0..n {
            for j in i + 1..n {
                for k in j + 1..n {
                    if nums[i] + nums[j] + nums[k] == 0 {
                        let mut t = [nums[i], nums[j], nums[k]];
                        t.sort();
                        want.insert(t);
                    }
                }
            }
        }
        check!(format!("nums = {nums:?}"), three_sum(&nums), want.into_iter().collect::<Vec<_>>());
    }
}

#[test]
fn scale_5000() {
    // Three odd numbers never sum to 0, so only the three far-away values at the end form a triplet.
    let mut rng = anneal_prelude::Rng::new(208);
    let mut nums: Vec<i32> = (0..5000).map(|i| 2 * i - 4999).collect();
    rng.shuffle(&mut nums);
    nums.extend_from_slice(&[-500_000, 1_000_000, -500_000]);
    check!("nums = the odd values -4999..=4999 shuffled, then -500000, 1000000, -500000", three_sum(&nums), vec![[-500_000, -500_000, 1_000_000]]);
}
