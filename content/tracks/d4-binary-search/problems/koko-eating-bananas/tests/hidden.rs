use solution::*;

#[test]
fn one_spare_hour() {
    check!(r#"[30,11,23,4,20], 6 hours"#, min_eating_speed(&[30, 11, 23, 4, 20], 6), Some(23));
}

#[test]
fn impossible() {
    check!(r#"[1,1,1], 2 hours"#, min_eating_speed(&[1, 1, 1], 2), None);
}

#[test]
fn huge_pile() {
    check!(r#"[10⁹], 2 hours"#, min_eating_speed(&[1_000_000_000], 2), Some(500_000_000));
}

#[test]
fn many_piles() {
    let v = vec![1_000_000_000u32; 100_000];
    check!(r#"10⁵ piles of 10⁹, 10¹⁴ hours"#, min_eating_speed(&v, 100_000_000_000_000), Some(1));
}

#[test]
fn no_piles() {
    check!(r#"[], 5 hours"#, min_eating_speed(&[], 5), None);
}

#[test]
fn one_hour_per_pile() {
    check!(r#"[3,9,4], 3 hours"#, min_eating_speed(&[3, 9, 4], 3), Some(9));
}

#[test]
fn max_pile_values() {
    check!(r#"[u32::MAX; 2], 4 hours"#, min_eating_speed(&[u32::MAX, u32::MAX], 4), Some(2_147_483_648));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(409);
    for _ in 0..400 {
        let n = rng.below(6);
        let piles: Vec<u32> = rng.vec(n, 1, 30);
        let hours = rng.int(0, 40) as u64;
        let top = piles.iter().copied().max().unwrap_or(0);
        let want = (1..=top).find(|&k| piles.iter().map(|&p| u64::from(p.div_ceil(k))).sum::<u64>() <= hours);
        check!(format!("piles = {piles:?}, hours = {hours}"), min_eating_speed(&piles, hours), want);
    }
}

#[test]
fn scale_big_answer() {
    // 10⁵ piles of 10⁹ with two hours each: the answer is 5·10⁸, far from 1.
    let v = vec![1_000_000_000u32; 100_000];
    check!("10⁵ piles of 10⁹, 2·10⁵ hours", min_eating_speed(&v, 200_000), Some(500_000_000));
}
