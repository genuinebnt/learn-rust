use solution::*;

#[test]
fn no_stones() {
    check!(r#"heights = [], k = 1"#, min_cost(&[], 1), 0);
}

#[test]
fn k_past_the_end() {
    check!(r#"heights = [10, 10], k = 100"#, min_cost(&[10, 10], 100), 0);
}

#[test]
fn zigzag() {
    check!(r#"heights = [30, 10, 60, 10, 60, 50], k = 2"#, min_cost(&[30, 10, 60, 10, 60, 50], 2), 40);
}

#[test]
fn k_one_walks() {
    check!(r#"heights = [10, 30, 40, 20], k = 1"#, min_cost(&[10, 30, 40, 20], 1), 50);
}

#[test]
fn negative_extremes() {
    check!(r#"heights = [-10⁹, 10⁹, -10⁹], k = 1"#, min_cost(&[-1_000_000_000, 1_000_000_000, -1_000_000_000], 1), 4_000_000_000);
}

#[test]
fn past_u32() {
    check!(r#"heights = [-10⁹, 10⁹] × 3, k = 1"#, min_cost(&[-1_000_000_000, 1_000_000_000, -1_000_000_000, 1_000_000_000, -1_000_000_000, 1_000_000_000], 1), 10_000_000_000);
}

#[test]
fn skip_the_spike() {
    check!(r#"heights = [0, 100, 0], k = 2"#, min_cost(&[0, 100, 0], 2), 0);
}

#[test]
fn random_vs_brute_force() {
    fn best(i: usize, h: &[i32], k: usize) -> u64 {
        if i + 1 == h.len() {
            return 0;
        }
        (i + 1..h.len().min(i + k + 1)).map(|j| h[i].abs_diff(h[j]) as u64 + best(j, h, k)).min().unwrap()
    }
    let mut rng = anneal_prelude::Rng::new(1256);
    for _ in 0..300 {
        let n = rng.int(1, 10) as usize;
        let heights: Vec<i32> = rng.vec(n, -20, 20);
        let k = rng.int(1, 4) as usize;
        check!(format!("heights = {heights:?}, k = {k}"), min_cost(&heights, k), best(0, &heights, k));
    }
}

#[test]
fn scale_deep_200000() {
    let heights: Vec<i32> = (0..200_000i64).map(|i| (i * 7919 % 10007 - 5000) as i32).collect();
    check!("heights[i] = (7919·i) % 10007 - 5000, 200000 stones, k = 2", min_cost(&heights, 2), 486_662_717);
}

#[test]
fn scale_wide_100000() {
    let heights: Vec<i32> = (0..100_000i64).map(|i| (i * 104_729 % 1_000_003) as i32).collect();
    check!("heights[i] = (104729·i) % 1000003, 100000 stones, k = 100", min_cost(&heights, 100), 12_970_165);
}
