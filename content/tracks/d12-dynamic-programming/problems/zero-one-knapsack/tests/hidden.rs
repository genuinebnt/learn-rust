use solution::*;

#[test]
fn no_items() {
    check!(r#"items = [], capacity = 0"#, knapsack(&[], 0), 0);
}

#[test]
fn too_heavy() {
    check!(r#"items = [(5, 10)], capacity = 4"#, knapsack(&[(5, 10)], 4), 0);
}

#[test]
fn weightless_item() {
    check!(r#"items = [(0, 5), (2, 3)], capacity = 1"#, knapsack(&[(0, 5), (2, 3)], 1), 5);
}

#[test]
fn exact_fit() {
    check!(r#"items = [(2, 3), (3, 4), (4, 5), (5, 6)], capacity = 5"#, knapsack(&[(2, 3), (3, 4), (4, 5), (5, 6)], 5), 7);
}

#[test]
fn duplicates() {
    check!(r#"items = [(3, 5); 4], capacity = 9"#, knapsack(&[(3, 5); 4], 9), 15);
}

#[test]
fn big_values() {
    check!(r#"items = [(1, 10⁹); 100], capacity = 100"#, knapsack(&[(1, 1_000_000_000); 100], 100), 100_000_000_000);
}

#[test]
fn everything_fits() {
    check!(r#"items = [(1, 2), (2, 3)], capacity = 100000"#, knapsack(&[(1, 2), (2, 3)], 100_000), 5);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1230);
    for _ in 0..300 {
        let n = rng.below(11);
        let mut items: Vec<(usize, u64)> = Vec::new();
        for _ in 0..n {
            let w = rng.int(0, 8) as usize;
            let v = rng.int(0, 20) as u64;
            items.push((w, v));
        }
        let cap = rng.int(0, 20) as usize;
        let mut want = 0;
        for mask in 0u32..(1 << n) {
            let (w, v) = (0..n).filter(|&i| mask >> i & 1 == 1).fold((0, 0), |(w, v), i| (w + items[i].0, v + items[i].1));
            if w <= cap {
                want = want.max(v);
            }
        }
        check!(format!("items = {items:?}, capacity = {cap}"), knapsack(&items, cap), want);
    }
}

#[test]
fn scale_100_items() {
    let items: Vec<(usize, u64)> = (0..100u64).map(|i| ((i * 7919 % 3000 + 500) as usize, i * 104_729 % 1000 + 1)).collect();
    check!("items[i] = ((7919·i) % 3000 + 500, (104729·i) % 1000 + 1), 100 items, capacity = 50000", knapsack(&items, 50_000), 25_744);
}
