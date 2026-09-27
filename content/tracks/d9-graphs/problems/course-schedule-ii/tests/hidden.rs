use solution::*;

/// "valid order", "no order", or what's wrong with the answer.
fn verdict(n: usize, prereqs: &[(usize, usize)], got: Option<Vec<usize>>) -> String {
    let Some(order) = got else {
        return "no order".to_string();
    };
    let mut pos = vec![usize::MAX; n];
    for (i, &c) in order.iter().enumerate() {
        if c >= n || pos[c] != usize::MAX {
            return format!("not a permutation of 0..{n}: {order:?}");
        }
        pos[c] = i;
    }
    if order.len() != n {
        return format!("only {} of {n} courses: {order:?}", order.len());
    }
    match prereqs.iter().find(|&&(a, b)| pos[a] > pos[b]) {
        Some(&(a, b)) => format!("{b} comes before its prerequisite {a}: {order:?}"),
        None => "valid order".to_string(),
    }
}

#[test]
fn self_loop() {
    check!(r#"n = 2, prereqs = [(1, 1)]"#, find_order(2, &[(1, 1)]), None);
}

#[test]
fn duplicate_prereqs() {
    let p = [(0, 2), (0, 2), (1, 2)];
    check!(r#"n = 3, prereqs = [(0, 2), (0, 2), (1, 2)]"#, verdict(3, &p, find_order(3, &p)), "valid order");
}

#[test]
fn cycle_off_to_the_side() {
    check!(r#"n = 5, prereqs = [(0, 1), (2, 3), (3, 4), (4, 2)]"#, find_order(5, &[(0, 1), (2, 3), (3, 4), (4, 2)]), None);
}

#[test]
fn reversed_chain() {
    check!(r#"n = 4, prereqs = [(3, 2), (2, 1), (1, 0)]"#, find_order(4, &[(3, 2), (2, 1), (1, 0)]), Some(vec![3, 2, 1, 0]));
}

#[test]
fn no_prereqs() {
    check!(r#"n = 4, prereqs = []"#, verdict(4, &[], find_order(4, &[])), "valid order");
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(946);
    for _ in 0..300 {
        let n = 1 + rng.below(7);
        let m = rng.below(9);
        let p: Vec<(usize, usize)> = (0..m).map(|_| (rng.below(n), rng.below(n))).collect();
        // Brute force: an order exists exactly when repeatedly removing unblocked courses empties the set.
        let mut left: Vec<usize> = (0..n).collect();
        while let Some(i) = left.iter().position(|&u| !p.iter().any(|&(a, b)| b == u && left.contains(&a))) {
            left.remove(i);
        }
        let want = if left.is_empty() { "valid order" } else { "no order" };
        check!(format!("n = {n}, prereqs = {p:?}"), verdict(n, &p, find_order(n, &p)), want);
    }
}

#[test]
fn scale_chain_200k() {
    let n = 200_000;
    let p: Vec<(usize, usize)> = (0..n - 1).map(|i| (i, i + 1)).collect();
    check!("n = 200000, chain 0 → 1 → … → 199999", verdict(n, &p, find_order(n, &p)), "valid order");
}

#[test]
fn scale_star_then_cycle() {
    // 0 before everything, and a cycle among the last three courses.
    let n = 200_000;
    let mut p: Vec<(usize, usize)> = (1..n).map(|i| (0, i)).collect();
    p.extend([(n - 3, n - 2), (n - 2, n - 1), (n - 1, n - 3)]);
    check!("n = 200000, 0 before all, cycle among the last three", find_order(n, &p), None);
}
