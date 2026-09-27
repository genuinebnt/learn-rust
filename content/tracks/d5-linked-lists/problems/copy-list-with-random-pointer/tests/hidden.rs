use solution::*;

#[test]
fn self_random() {
    let spec = [(1, Some(0)), (2, Some(1))];
    check!(r#"[(1,0),(2,1)]"#, to_arena(&build(&spec)), spec.to_vec());
}

#[test]
fn single_self() {
    let spec = [(4, Some(0))];
    check!(r#"[(4,0)]"#, to_arena(&build(&spec)), spec.to_vec());
}

#[test]
fn all_to_last() {
    let spec = [(1, Some(3)), (2, Some(3)), (3, Some(3)), (4, Some(3))];
    check!(r#"four nodes, every random → 3"#, to_arena(&build(&spec)), spec.to_vec());
}

#[test]
fn extremes() {
    let spec = [(i32::MIN, Some(1)), (i32::MAX, Some(0))];
    check!(r#"[(MIN,1),(MAX,0)]"#, to_arena(&build(&spec)), spec.to_vec());
}

#[test]
fn list_unchanged() {
    let spec = [(1, Some(2)), (2, None), (3, Some(0))];
    let head = build(&spec);
    check!(r#"the list reads the same afterwards"#, (to_arena(&head), to_arena(&head)), (spec.to_vec(), spec.to_vec()));
}

/// Unlinks a long Rc list one node at a time (the default drop recurses once per node).
fn free(mut cur: RLink) {
    while let Some(node) = cur {
        cur = node.borrow_mut().next.take();
    }
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(511);
    for _ in 0..300 {
        let n = rng.below(8);
        let spec: Vec<(i32, Option<usize>)> = (0..n).map(|_| (rng.int(0, 2) as i32, if rng.bool() { Some(rng.below(n)) } else { None })).collect();
        check!(format!("{spec:?}"), to_arena(&build(&spec)), spec.clone());
    }
}

#[test]
fn scale_100k() {
    let n = 100_000;
    let spec: Vec<(i32, Option<usize>)> = (0..n).map(|i| (7, Some((i * 7_919 + 13) % n))).collect();
    let head = build(&spec);
    let got = to_arena(&head);
    free(head);
    check!("100000 nodes, all value 7, random = (7919 i + 13) % n", got == spec, true);
}

#[test]
fn equal_values() {
    let spec = [(5, Some(2)), (5, None), (5, Some(0))];
    check!(r#"three nodes with value 5"#, to_arena(&build(&spec)), spec.to_vec());
}

#[test]
fn long() {
    let spec: Vec<(i32, Option<usize>)> = (0..2_000).map(|i| (i as i32, Some(1_999 - i))).collect();
    check!(r#"2000 nodes, random = reversed index"#, to_arena(&build(&spec)) == spec, true);
}
