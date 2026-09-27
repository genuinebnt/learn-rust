use solution::*;

#[test]
fn single_node() {
    let mut t = Tree::new();
    t.insert(7);
    check!(r#"insert 7"#, (t.contains(7), t.in_order(), t.nodes[0].left.is_none() && t.nodes[0].right.is_none()), (true, vec![7], true));
}

#[test]
fn extreme_keys() {
    let mut t = Tree::new();
    for k in [i32::MIN, i32::MAX, 0] {
        t.insert(k);
    }
    check!(r#"insert i32::MIN, i32::MAX, 0"#, t.in_order(), vec![i32::MIN, 0, i32::MAX]);
}

#[test]
fn duplicates_ignored() {
    let mut t = Tree::new();
    for _ in 0..3 {
        t.insert(1);
    }
    check!(r#"insert 1, 1, 1"#, (t.nodes.len(), t.in_order()), (1, vec![1]));
}

#[test]
fn sorted_inserts_make_a_right_spine() {
    let mut t = Tree::new();
    for k in 1..=5 {
        t.insert(k);
    }
    check!(r#"insert 1..=5"#, (t.in_order(), t.nodes.iter().all(|n| n.left.is_none())), (vec![1, 2, 3, 4, 5], true));
}

#[test]
fn reverse_inserts_make_a_left_spine() {
    let mut t = Tree::new();
    for k in (1..=5).rev() {
        t.insert(k);
    }
    check!(r#"insert 5, 4, 3, 2, 1"#, (t.in_order(), t.nodes.iter().all(|n| n.right.is_none())), (vec![1, 2, 3, 4, 5], true));
}

#[test]
fn zero_key_is_an_ordinary_key() {
    let mut t = Tree::new();
    for k in [0, -1, 1] {
        t.insert(k);
    }
    check!(r#"insert 0, -1, 1"#, (t.contains(0), t.contains(-1), t.contains(1), t.contains(2)), (true, true, true, false));
}

#[test]
fn vec_of_nodes_is_smaller() {
    check!(r#"size_of::<Node>() * 1000"#, std::mem::size_of::<Node>() * 1000, 12_000);
}

#[test]
fn mixed_signs() {
    let mut t = Tree::new();
    for k in [-5, 5, -3, 3, 0] {
        t.insert(k);
    }
    check!(r#"insert -5, 5, -3, 3, 0"#, (t.in_order(), t.contains(-3), t.contains(-4)), (vec![-5, -3, 0, 3, 5], true, false));
}

#[test]
fn random_vs_btreeset() {
    let mut rng = anneal_prelude::Rng::new(7108);
    for _ in 0..300 {
        let n = rng.below(20);
        let keys: Vec<i32> = rng.vec(n, -10, 10);
        let mut t = Tree::new();
        let mut model = std::collections::BTreeSet::new();
        for &k in &keys {
            check!(format!("insert {k} after {model:?}"), t.insert(k), model.insert(k));
        }
        check!(format!("in_order after inserting {keys:?}"), t.in_order(), model.iter().copied().collect::<Vec<_>>());
        let q = rng.int(-11, 11) as i32;
        check!(format!("contains {q} after inserting {keys:?}"), t.contains(q), model.contains(&q));
    }
}

#[test]
fn scale_past_u16() {
    let mut rng = anneal_prelude::Rng::new(7109);
    let mut keys: Vec<i32> = (0..150_000).map(|i| i * 3).collect();
    rng.shuffle(&mut keys);
    let mut t = Tree::new();
    for &k in &keys {
        t.insert(k);
    }
    let hits = (0..450_000).filter(|&k| t.contains(k)).count();
    let sorted = t.in_order();
    check!("150000 shuffled keys 0, 3, 6, …: hits among 0..450000, and in_order", (hits, sorted.len(), sorted[149_999], sorted.windows(2).all(|w| w[0] < w[1])), (150_000, 150_000, 449_997, true));
}
