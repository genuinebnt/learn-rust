use solution::*;

#[test]
fn no_projects() {
    check!(r#"k = 4, w = 3, profits = [], capital = []"#, find_maximized_capital(4, 3, &[], &[]), 3);
}

#[test]
fn capital_exactly_w() {
    check!(r#"k = 1, w = 5, profits = [2], capital = [5]"#, find_maximized_capital(1, 5, &[2], &[5]), 7);
}

#[test]
fn zero_profit_projects() {
    check!(r#"k = 3, w = 0, profits = [0, 0, 0], capital = [0, 0, 1]"#, find_maximized_capital(3, 0, &[0, 0, 0], &[0, 0, 1]), 0);
}

#[test]
fn several_unlock_at_once() {
    check!(r#"k = 2, w = 0, profits = [1, 3, 5, 2], capital = [0, 1, 1, 1]"#, find_maximized_capital(2, 0, &[1, 3, 5, 2], &[0, 1, 1, 1]), 6);
}

#[test]
fn past_u32() {
    check!(r#"k = 3, w = 4000000000, profits = [10⁹; 3], capital = [0; 3]"#, find_maximized_capital(3, 4_000_000_000, &[1_000_000_000; 3], &[0; 3]), 7_000_000_000);
}

#[test]
fn chain() {
    check!(r#"k = 4, w = 1, profits = [1, 2, 4, 8], capital = [1, 2, 4, 8]"#, find_maximized_capital(4, 1, &[1, 2, 4, 8], &[1, 2, 4, 8]), 16);
}

#[test]
fn best_affordable_not_best_overall() {
    check!(r#"k = 1, w = 2, profits = [3, 100], capital = [2, 3]"#, find_maximized_capital(1, 2, &[3, 100], &[2, 3]), 5);
}

#[test]
fn k_larger_than_n() {
    check!(r#"k = 100, w = 0, profits = [1, 2], capital = [0, 0]"#, find_maximized_capital(100, 0, &[1, 2], &[0, 0]), 3);
}

#[test]
fn random_vs_brute_force() {
    // Try every order of every affordable project, up to k of them.
    fn best(k: usize, w: u64, profits: &[u64], capital: &[u64], used: &mut [bool]) -> u64 {
        let mut out = w;
        if k == 0 {
            return out;
        }
        for i in 0..profits.len() {
            if !used[i] && capital[i] <= w {
                used[i] = true;
                out = out.max(best(k - 1, w + profits[i], profits, capital, used));
                used[i] = false;
            }
        }
        out
    }
    let mut rng = anneal_prelude::Rng::new(716);
    for _ in 0..300 {
        let n = rng.below(7);
        let profits: Vec<u64> = rng.vec(n, 0, 6);
        let capital: Vec<u64> = rng.vec(n, 0, 8);
        let k = rng.below(5);
        let w = rng.int(0, 3) as u64;
        let want = best(k, w, &profits, &capital, &mut vec![false; n]);
        check!(format!("k = {k}, w = {w}, profits = {profits:?}, capital = {capital:?}"), find_maximized_capital(k, w, &profits, &capital), want);
    }
}

#[test]
fn scale_100k_projects() {
    let mut rng = anneal_prelude::Rng::new(717);
    let n = 100_000;
    let profits: Vec<u64> = rng.vec(n, 1, 1000);
    // Every 1000th project is free, so there is always somewhere to start.
    let capital: Vec<u64> = (0..n).map(|i| if i % 1000 == 0 { 0 } else { rng.int(0, 40_000_000) as u64 }).collect();
    let k = 50_000;
    // Reference: the same greedy with a sorted Vec and a BTreeMap multiset of affordable profits.
    let mut order: Vec<usize> = (0..n).collect();
    order.sort_unstable_by_key(|&i| capital[i]);
    let mut bag = std::collections::BTreeMap::new();
    let (mut w, mut next) = (0u64, 0);
    for _ in 0..k {
        while next < n && capital[order[next]] <= w {
            *bag.entry(profits[order[next]]).or_insert(0u32) += 1;
            next += 1;
        }
        let Some(mut e) = bag.last_entry() else { break };
        w += *e.key();
        *e.get_mut() -= 1;
        if *e.get() == 0 {
            e.remove();
        }
    }
    check!("n = 100000 random projects (profit 1..=1000, capital 0..=4·10⁷, every 1000th free), k = 50000, w = 0", find_maximized_capital(k, 0, &profits, &capital), w);
}
