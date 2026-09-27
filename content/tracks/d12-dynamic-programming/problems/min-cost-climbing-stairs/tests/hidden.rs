use solution::*;

#[test]
fn empty() {
    check!(r#"cost = []"#, min_cost_climbing_stairs(&[]), 0);
}

#[test]
fn single() {
    check!(r#"cost = [9]"#, min_cost_climbing_stairs(&[9]), 0);
}

#[test]
fn zeros() {
    check!(r#"cost = [0, 0, 0, 0]"#, min_cost_climbing_stairs(&[0, 0, 0, 0]), 0);
}

#[test]
fn start_on_one() {
    check!(r#"cost = [100, 1, 100]"#, min_cost_climbing_stairs(&[100, 1, 100]), 1);
}

#[test]
fn start_on_zero() {
    check!(r#"cost = [1, 100, 1, 100]"#, min_cost_climbing_stairs(&[1, 100, 1, 100]), 2);
}

#[test]
fn skip_the_last() {
    check!(r#"cost = [1, 1, 9]"#, min_cost_climbing_stairs(&[1, 1, 9]), 1);
}

#[test]
fn all_max() {
    check!(r#"cost = [10000; 6]"#, min_cost_climbing_stairs(&[10_000; 6]), 30_000);
}

#[test]
fn past_u32() {
    check!(r#"cost = [10000; 1000000]"#, min_cost_climbing_stairs(&vec![10_000; 1_000_000]), 5_000_000_000);
}

#[test]
fn random_vs_brute_force() {
    fn best(cost: &[u32], at: usize) -> u64 {
        if at >= cost.len() { return 0; }
        cost[at] as u64 + best(cost, at + 1).min(best(cost, at + 2))
    }
    let mut rng = anneal_prelude::Rng::new(1203);
    for _ in 0..300 {
        let n = rng.below(16);
        let cost: Vec<u32> = rng.vec(n, 0, 20);
        let want = best(&cost, 0).min(best(&cost, 1));
        check!(format!("cost = {cost:?}"), min_cost_climbing_stairs(&cost), want);
    }
}

#[test]
fn scale_200k() {
    let cost: Vec<u32> = (0..200_000u32).map(|i| (i * 7919) % 10_000).collect();
    check!("cost[i] = (7919·i) % 10000, 200000 steps", min_cost_climbing_stairs(&cost), 427_375_280);
}
