use solution::*;

#[test]
fn all_equal() {
    check!(r#"[1,1,1], k = 2"#, smallest_distance_pair(&[1, 1, 1], 2), 0);
}

#[test]
fn extremes() {
    check!(r#"[i32::MIN, i32::MAX], k = 1"#, smallest_distance_pair(&[i32::MIN, i32::MAX], 1), u32::MAX);
}

#[test]
fn many() {
    let v: Vec<i32> = (0..10_000).collect();
    check!(r#"0..10⁴, k = 10⁶"#, smallest_distance_pair(&v, 1_000_000), 101);
}

#[test]
fn negatives() {
    check!(r#"[-3,-1,4], k = 2"#, smallest_distance_pair(&[-3, -1, 4], 2), 5);
}

#[test]
fn k_is_the_last_pair() {
    check!(r#"[1,5,9,20], k = 6"#, smallest_distance_pair(&[1, 5, 9, 20], 6), 19);
}

#[test]
fn unsorted_input() {
    check!(r#"[9,1,5], k = 1 and k = 2"#, (smallest_distance_pair(&[9, 1, 5], 1), smallest_distance_pair(&[9, 1, 5], 2)), (4, 4));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(413);
    for _ in 0..400 {
        let n = 2 + rng.below(8);
        let nums: Vec<i32> = rng.vec(n, -20, 20);
        let mut all: Vec<u32> = (0..n).flat_map(|i| (i + 1..n).map(move |j| (i, j))).map(|(i, j)| nums[i].abs_diff(nums[j])).collect();
        all.sort_unstable();
        let k = 1 + rng.below(all.len());
        check!(format!("nums = {nums:?}, k = {k}"), smallest_distance_pair(&nums, k), all[k - 1]);
    }
}

#[test]
fn scale_100k() {
    // 0..100000 shuffled; pairs with distance ≤ d number d·n − d(d+1)/2.
    let mut v: Vec<i32> = (0..100_000).collect();
    anneal_prelude::Rng::new(414).shuffle(&mut v);
    check!("a shuffle of 0..100000, k = 2.5·10⁹", smallest_distance_pair(&v, 2_500_000_000), 29_290);
}
