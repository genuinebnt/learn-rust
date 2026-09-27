use solution::*;

#[test]
fn each_alone() {
    check!(r#"[1,4,4], k = 3"#, split_array(&[1, 4, 4], 3), 4);
}

#[test]
fn one_part() {
    check!(r#"[1,2,3], k = 1"#, split_array(&[1, 2, 3], 1), 6);
}

#[test]
fn big_values() {
    check!(r#"[4·10⁹; 4], k = 2"#, split_array(&[4_000_000_000, 4_000_000_000, 4_000_000_000, 4_000_000_000], 2), 8_000_000_000);
}

#[test]
fn long() {
    let v = vec![1u32; 100_000];
    check!(r#"10⁵ ones, k = 7"#, split_array(&v, 7), 14_286);
}

#[test]
fn single() {
    check!(r#"[7], k = 1"#, split_array(&[7], 1), 7);
}

#[test]
fn all_zero() {
    check!(r#"[0,0,0], k = 2"#, split_array(&[0, 0, 0], 2), 0);
}

#[test]
fn u32_max_values() {
    let v = [u32::MAX; 3];
    check!(r#"[u32::MAX; 3], k = 1 and k = 3"#, (split_array(&v, 1), split_array(&v, 3)), (12_884_901_885, 4_294_967_295));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(412);
    for _ in 0..400 {
        let n = 1 + rng.below(8);
        let nums: Vec<u32> = rng.vec(n, 0, 20);
        let k = 1 + rng.below(n);
        // Brute force: DP over (prefix length, parts used).
        let mut best = vec![vec![u64::MAX; k + 1]; n + 1];
        best[0][0] = 0;
        for i in 1..=n {
            for p in 1..=k.min(i) {
                for j in p - 1..i {
                    if best[j][p - 1] != u64::MAX {
                        let part: u64 = nums[j..i].iter().map(|&x| u64::from(x)).sum();
                        best[i][p] = best[i][p].min(best[j][p - 1].max(part));
                    }
                }
            }
        }
        check!(format!("nums = {nums:?}, k = {k}"), split_array(&nums, k), best[n][k]);
    }
}

#[test]
fn scale_100k_values() {
    let mut x: u64 = 5;
    let v: Vec<u32> = (0..100_000).map(|_| { x = x.wrapping_mul(6_364_136_223_846_793_005).wrapping_add(1_442_695_040_888_963_407); ((x >> 33) % 1_000_000_000) as u32 }).collect();
    check!("10⁵ pseudo-random values below 10⁹ (LCG seed 5), k = 50", split_array(&v, 50), 943_751_813_026);
}
