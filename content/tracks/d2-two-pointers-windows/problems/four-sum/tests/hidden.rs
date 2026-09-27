use solution::*;

#[test]
fn overflow() {
    check!(r#"nums = [1e9 × 4], target = 4e9"#, four_sum(&[1_000_000_000; 4], 4_000_000_000), vec![[1_000_000_000; 4]]);
}

#[test]
fn too_short() {
    check!(r#"nums = [1, 2, 3], target = 6"#, four_sum(&[1, 2, 3], 6), Vec::<[i32; 4]>::new());
}

#[test]
fn empty() {
    check!(r#"nums = [], target = 0"#, four_sum(&[], 0), Vec::<[i32; 4]>::new());
}

#[test]
fn exactly_four() {
    check!(r#"nums = [4, -1, 3, 0], target = 6"#, four_sum(&[4, -1, 3, 0], 6), vec![[-1, 0, 3, 4]]);
}

#[test]
fn negative_target() {
    check!(r#"nums = [-3, -2, -1, 0, 0, 1, 2, 3], target = -6"#, four_sum(&[-3, -2, -1, 0, 0, 1, 2, 3], -6), vec![[-3, -2, -1, 0]]);
}

#[test]
fn many_zeros() {
    check!(r#"nums = [0; 500], target = 0"#, four_sum(&vec![0; 500], 0), vec![[0, 0, 0, 0]]);
}

#[test]
fn below_i32_min() {
    check!(r#"nums = [-1e9 × 4, 1e9], target = -4e9"#, four_sum(&[-1_000_000_000, -1_000_000_000, -1_000_000_000, -1_000_000_000, 1_000_000_000], -4_000_000_000), vec![[-1_000_000_000; 4]]);
}

#[test]
fn target_out_of_i32() {
    check!(r#"nums = [1e9 × 4], target = -294967296"#, four_sum(&[1_000_000_000; 4], -294_967_296), Vec::<[i32; 4]>::new());
}

#[test]
fn dedup_second_value() {
    check!(r#"nums = [-1, 0, 0, 0, 1, 1], target = 1"#, four_sum(&[-1, 0, 0, 0, 1, 1], 1), vec![[-1, 0, 1, 1], [0, 0, 0, 1]]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(219);
    for _ in 0..300 {
        let n = rng.below(9);
        let nums: Vec<i32> = rng.vec(n, -4, 4);
        let target = rng.int(-6, 6);
        let mut want = std::collections::BTreeSet::new();
        for a in 0..n {
            for b in a + 1..n {
                for c in b + 1..n {
                    for d in c + 1..n {
                        if (nums[a] + nums[b] + nums[c] + nums[d]) as i64 == target {
                            let mut q = [nums[a], nums[b], nums[c], nums[d]];
                            q.sort();
                            want.insert(q);
                        }
                    }
                }
            }
        }
        check!(format!("nums = {nums:?}, target = {target}"), four_sum(&nums, target), want.into_iter().collect::<Vec<_>>());
    }
}

#[test]
fn scale_600() {
    // Every value is 1 more than a multiple of 4, so four of them sum to a multiple of 4 and never to 2.
    let mut rng = anneal_prelude::Rng::new(220);
    let mut nums: Vec<i32> = (0..600).map(|i| 4 * i - 1199).collect();
    rng.shuffle(&mut nums);
    check!("nums = 4i - 1199 for i in 0..600, shuffled, target = 2", four_sum(&nums, 2), Vec::<[i32; 4]>::new());
}
