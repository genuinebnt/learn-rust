use solution::*;

#[test]
fn swap_pair() {
    check!(r#"costs = [(5, 1), (1, 5)]"#, two_city_sched_cost(&[(5, 1), (1, 5)]), 2);
}

#[test]
fn all_equal() {
    check!(r#"costs = [(3, 3); 4]"#, two_city_sched_cost(&[(3, 3); 4]), 12);
}

#[test]
fn a_cheaper_for_all() {
    check!(r#"costs = [(1, 10), (2, 20), (3, 30), (4, 40)]"#, two_city_sched_cost(&[(1, 10), (2, 20), (3, 30), (4, 40)]), 37);
}

#[test]
fn u32_extremes() {
    check!(r#"costs = [(4294967295, 0), (0, 4294967295)]"#, two_city_sched_cost(&[(u32::MAX, 0), (0, u32::MAX)]), 0);
}

#[test]
fn total_past_u32() {
    check!(r#"costs = [(4294967295, 4294967295); 4]"#, two_city_sched_cost(&[(u32::MAX, u32::MAX); 4]), 17_179_869_180);
}

#[test]
fn sort_by_a_trap() {
    check!(r#"costs = [(1, 2), (2, 100)]"#, two_city_sched_cost(&[(1, 2), (2, 100)]), 4);
}

#[test]
fn zeros() {
    check!(r#"costs = [(0, 0), (0, 0)]"#, two_city_sched_cost(&[(0, 0), (0, 0)]), 0);
}

#[test]
fn six_with_ties() {
    check!(r#"costs = [(10, 20), (30, 200), (400, 50), (30, 20), (1, 1), (1, 1)]"#, two_city_sched_cost(&[(10, 20), (30, 200), (400, 50), (30, 20), (1, 1), (1, 1)]), 112);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(819);
    for _ in 0..300 {
        let n = 2 * rng.below(6);
        let costs: Vec<(u32, u32)> = (0..n).map(|_| (rng.int(0, 20) as u32, rng.int(0, 20) as u32)).collect();
        // Every way to send exactly half to A.
        let mut want = u64::MAX;
        for mask in 0u32..1 << n {
            if mask.count_ones() as usize == n / 2 {
                let total: u64 = (0..n).map(|i| (if mask >> i & 1 == 1 { costs[i].0 } else { costs[i].1 }) as u64).sum();
                want = want.min(total);
            }
        }
        check!(format!("costs = {costs:?}"), two_city_sched_cost(&costs), want);
    }
}

#[test]
fn scale_200k() {
    let costs: Vec<(u32, u32)> = (0..200_000u32).rev().map(|i| (i, 200_000 - i)).collect();
    check!("costs[i] = (i, 200000 - i) for i in 0..200000, reversed", two_city_sched_cost(&costs), 10_000_000_000);
}
