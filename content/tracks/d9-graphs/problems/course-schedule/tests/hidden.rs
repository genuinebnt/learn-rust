use solution::*;

#[test]
fn self_loop() {
    check!(r#"n = 1, prereqs = [(0, 0)]"#, can_finish(1, &[(0, 0)]), false);
}

#[test]
fn cycle_off_to_the_side() {
    check!(r#"n = 4, prereqs = [(0, 1), (2, 3), (3, 2)]"#, can_finish(4, &[(0, 1), (2, 3), (3, 2)]), false);
}

#[test]
fn long_chain() {
    let chain: Vec<(usize, usize)> = (0..99_999).map(|i| (i, i + 1)).collect();
    check!(r#"n = 10⁵, chain 0 → 1 → … → 99999"#, can_finish(100_000, &chain), true);
}

#[test]
fn single() {
    check!(r#"n = 1, prereqs = []"#, can_finish(1, &[]), true);
}

#[test]
fn duplicate_prereq() {
    check!(r#"n = 2, prereqs = [(0, 1), (0, 1)]"#, can_finish(2, &[(0, 1), (0, 1)]), true);
}

#[test]
fn three_cycle_with_tail() {
    check!(r#"n = 5, prereqs = [(0, 1), (1, 2), (2, 0), (3, 4)]"#, can_finish(5, &[(0, 1), (1, 2), (2, 0), (3, 4)]), false);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(912);
    for _ in 0..300 {
        let n = 1 + rng.below(7);
        let m = rng.below(9);
        let prereqs: Vec<(usize, usize)> = (0..m).map(|_| (rng.below(n), rng.below(n))).collect();
        // Brute force: keep removing a course none of the remaining courses points at.
        let mut left: Vec<usize> = (0..n).collect();
        while let Some(pos) = left.iter().position(|&u| !prereqs.iter().any(|&(a, b)| b == u && left.contains(&a))) {
            left.remove(pos);
        }
        check!(format!("n = {n}, prereqs = {prereqs:?}"), can_finish(n, &prereqs), left.is_empty());
    }
}

#[test]
fn scale_reversed_chain_200k() {
    let n = 200_000;
    let chain: Vec<(usize, usize)> = (0..n - 1).map(|i| (i + 1, i)).collect();
    check!("n = 200000, chain 199999 → … → 1 → 0", can_finish(n, &chain), true);
}

#[test]
fn scale_one_big_cycle() {
    let n = 200_000;
    let edges: Vec<(usize, usize)> = (0..n).map(|i| (i, (i + 1) % n)).collect();
    check!("n = 200000, one cycle through every course", can_finish(n, &edges), false);
}
