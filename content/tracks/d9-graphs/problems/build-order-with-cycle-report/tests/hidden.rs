use solution::*;

#[test]
fn no_deps() {
    check!(r#"n = 3, deps = []"#, build_order(3, &[]), Ok(vec![0, 1, 2]));
}

#[test]
fn smallest_first() {
    check!(r#"n = 3, deps = [(2, 1)]"#, build_order(3, &[(2, 1)]), Ok(vec![0, 2, 1]));
}

#[test]
fn all_stuck() {
    check!(r#"n = 2, deps = [(0, 1), (1, 0)]"#, build_order(2, &[(0, 1), (1, 0)]), Err(vec![0, 1]));
}

#[test]
fn downstream_of_a_cycle() {
    check!(r#"n = 5, deps = [(1, 2), (2, 1), (2, 3), (0, 4)]"#, build_order(5, &[(1, 2), (2, 1), (2, 3), (0, 4)]), Err(vec![1, 2, 3]));
}

#[test]
fn duplicate_dependency() {
    check!(r#"n = 2, deps = [(0, 1), (0, 1)]"#, build_order(2, &[(0, 1), (0, 1)]), Ok(vec![0, 1]));
}

#[test]
fn reversed_numbers() {
    check!(r#"n = 3, deps = [(2, 1), (1, 0)]"#, build_order(3, &[(2, 1), (1, 0)]), Ok(vec![2, 1, 0]));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(913);
    for _ in 0..300 {
        let n = 1 + rng.below(7);
        let m = rng.below(9);
        let deps: Vec<(usize, usize)> = (0..m).map(|_| (rng.below(n), rng.below(n))).collect();
        // Brute force: build the smallest package whose dependencies are all built.
        let mut built = vec![false; n];
        let mut order = Vec::new();
        while let Some(u) = (0..n).find(|&u| !built[u] && deps.iter().all(|&(a, b)| b != u || built[a])) {
            built[u] = true;
            order.push(u);
        }
        let want = if order.len() == n { Ok(order) } else { Err((0..n).filter(|&u| !built[u]).collect()) };
        check!(format!("n = {n}, deps = {deps:?}"), build_order(n, &deps), want);
    }
}

#[test]
fn scale_reversed_chain_200k() {
    let n = 200_000;
    let deps: Vec<(usize, usize)> = (0..n - 1).map(|i| (i + 1, i)).collect();
    let out = build_order(n, &deps).unwrap();
    check!("n = 200000, deps = [(i + 1, i)]", (out.len(), out[0], out[n - 1]), (n, n - 1, 0));
}

#[test]
fn scale_cycle_at_the_end() {
    // 0 → 1 → … → 199999 → 199998: everything before 199998 builds.
    let n = 200_000;
    let mut deps: Vec<(usize, usize)> = (0..n - 1).map(|i| (i, i + 1)).collect();
    deps.push((n - 1, n - 2));
    check!("n = 200000, chain with a cycle between the last two", build_order(n, &deps), Err(vec![n - 2, n - 1]));
}
