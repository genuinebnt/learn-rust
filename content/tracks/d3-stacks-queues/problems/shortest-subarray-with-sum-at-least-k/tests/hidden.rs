use solution::*;

#[test]
fn empty() {
    check!(r#"[], k = 1"#, shortest_subarray(&[], 1), None);
}

#[test]
fn all_negative() {
    check!(r#"[-1,-2], k = 1"#, shortest_subarray(&[-1, -2], 1), None);
}

#[test]
fn alternating() {
    check!(r#"[1,-1,1,-1,1], k = 1"#, shortest_subarray(&[1, -1, 1, -1, 1], 1), Some(1));
}

#[test]
fn two_windows() {
    check!(r#"[-1,5,-1,5], k = 9"#, shortest_subarray(&[-1, 5, -1, 5], 9), Some(3));
}

#[test]
fn best_is_not_first() {
    check!(r#"[48,99,37,4,-31], k = 140"#, shortest_subarray(&[48, 99, 37, 4, -31], 140), Some(2));
}

#[test]
fn drop_after_peak() {
    check!(r#"[17,85,93,-45,-21], k = 150"#, shortest_subarray(&[17, 85, 93, -45, -21], 150), Some(2));
}

#[test]
fn large_values() {
    check!(r#"[10⁹, 10⁹, 10⁹], k = 3·10⁹"#, shortest_subarray(&[1_000_000_000, 1_000_000_000, 1_000_000_000], 3_000_000_000), Some(3));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(3014);
    for _ in 0..400 {
        let n = rng.below(10);
        let nums: Vec<i64> = rng.vec(n, -10, 10);
        let k = rng.int(1, 20);
        let mut want: Option<usize> = None;
        for i in 0..n {
            let mut sum = 0;
            for j in i..n {
                sum += nums[j];
                if sum >= k && want.is_none_or(|w| j - i + 1 < w) {
                    want = Some(j - i + 1);
                }
            }
        }
        check!(format!("nums = {nums:?}, k = {k}"), shortest_subarray(&nums, k), want);
    }
}

#[test]
fn scale_200k_unreachable() {
    let v = vec![1i64; 200_000];
    check!("200000 ones, k = 10⁹", shortest_subarray(&v, 1_000_000_000), None);
}

#[test]
fn negative_prefix() {
    check!(r#"[-28,81,-20,28,-29], k = 89"#, shortest_subarray(&[-28, 81, -20, 28, -29], 89), Some(3));
}

#[test]
fn big() {
    let mut v = vec![1i64; 100_000];
    v[99_998] = 1_500_000_000;
    v[99_999] = 1_500_000_000;
    check!(r#"10⁵ values, k needs the last two"#, shortest_subarray(&v, 3_000_000_000), Some(2));
}
