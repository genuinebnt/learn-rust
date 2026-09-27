use solution::*;

#[test]
fn all_zero() {
    check!(r#"gas = [0], cost = [0]"#, can_complete_circuit(&[0], &[0]), Some(0));
}

#[test]
fn start_at_the_last() {
    check!(r#"gas = [0, 0, 5], cost = [1, 1, 1]"#, can_complete_circuit(&[0, 0, 5], &[1, 1, 1]), Some(2));
}

#[test]
fn start_at_the_first() {
    check!(r#"gas = [3, 1, 1], cost = [1, 2, 2]"#, can_complete_circuit(&[3, 1, 1], &[1, 2, 2]), Some(0));
}

#[test]
fn short_by_one() {
    check!(r#"gas = [1, 2, 3, 4, 5], cost = [3, 4, 5, 1, 3]"#, can_complete_circuit(&[1, 2, 3, 4, 5], &[3, 4, 5, 1, 3]), None);
}

#[test]
fn tank_past_i32() {
    check!(r#"gas = [1000000000, 1000000000, 1000000000, 0, 0, 0], cost = [0, 0, 0, 1000000000, 1000000000, 1000000000]"#, can_complete_circuit(&[1_000_000_000, 1_000_000_000, 1_000_000_000, 0, 0, 0], &[0, 0, 0, 1_000_000_000, 1_000_000_000, 1_000_000_000]), Some(0));
}

#[test]
fn two_resets() {
    check!(r#"gas = [5, 1, 2, 3, 4], cost = [4, 4, 1, 5, 1]"#, can_complete_circuit(&[5, 1, 2, 3, 4], &[4, 4, 1, 5, 1]), Some(4));
}

#[test]
fn three_resets() {
    check!(r#"gas = [1, 1, 1, 10], cost = [2, 2, 2, 1]"#, can_complete_circuit(&[1, 1, 1, 10], &[2, 2, 2, 1]), Some(3));
}

#[test]
fn dips_to_zero() {
    check!(r#"gas = [2, 0, 1], cost = [1, 1, 1]"#, can_complete_circuit(&[2, 0, 1], &[1, 1, 1]), Some(0));
}

#[test]
fn total_short_by_one_at_scale() {
    check!(r#"gas = [999999999, 0], cost = [0, 1000000000]"#, can_complete_circuit(&[999_999_999, 0], &[0, 1_000_000_000]), None);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(816);
    for _ in 0..400 {
        let n = 1 + rng.below(7);
        let gas: Vec<u32> = rng.vec(n, 0, 4);
        let cost: Vec<u32> = rng.vec(n, 0, 4);
        // Drive around from every start.
        let want = (0..n).find(|&s| {
            let mut tank = 0i64;
            (0..n).all(|k| {
                let i = (s + k) % n;
                tank += gas[i] as i64 - cost[i] as i64;
                tank >= 0
            })
        });
        check!(format!("gas = {gas:?}, cost = {cost:?}"), can_complete_circuit(&gas, &cost), want);
    }
}

#[test]
fn scale_200k() {
    // Every start before 199998 drives a long way, then runs dry at station 199998.
    let n = 200_000usize;
    let mut gas = vec![1u32; n];
    let mut cost = vec![0u32; n];
    gas[n - 2] = 0;
    cost[n - 2] = (n - 1) as u32;
    gas[n - 1] = (n - 1) as u32;
    let mut short = gas.clone();
    short[n - 1] = 0;
    check!(
        "gas = [1, …, 1, 0, 199999], cost = [0, …, 0, 199999, 0]; then gas[199999] = 0",
        (can_complete_circuit(&gas, &cost), can_complete_circuit(&short, &cost)),
        (Some(199_999), None)
    );
}
