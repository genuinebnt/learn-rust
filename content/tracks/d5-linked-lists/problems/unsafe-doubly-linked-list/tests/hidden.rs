use solution::*;

#[test]
fn empty() {
    let mut l = LinkedList::new();
    check!(r#"new list"#, (l.pop_front(), l.pop_back(), l.iter().next(), l.is_empty()), (None, None, None, true));
}

#[test]
fn iter_after_pops() {
    let mut l = LinkedList::new();
    for i in 0..6 {
        l.push_back(i);
    }
    check!(r#"push_back 0..6; pop_front, pop_back; iter"#, { l.pop_front(); l.pop_back(); l.iter().copied().collect::<Vec<_>>() }, vec![1, 2, 3, 4]);
}

#[test]
fn len_tracks() {
    let mut l = LinkedList::new();
    check!(r#"push 3, pop 1"#, { l.push_back(1); l.push_front(0); l.push_back(2); l.pop_front(); (l.len(), l.is_empty()) }, (2, false));
}

#[test]
fn extremes() {
    let mut l = LinkedList::new();
    l.push_back(i32::MAX);
    l.push_front(i32::MIN);
    check!(r#"push i32::MIN front, i32::MAX back"#, l.iter().copied().collect::<Vec<_>>(), vec![i32::MIN, i32::MAX]);
}

#[test]
fn two_iters() {
    let mut l = LinkedList::new();
    for i in 1..=3 {
        l.push_back(i);
    }
    check!(r#"two iterators over the same list at once"#, l.iter().zip(l.iter().skip(1)).map(|(a, b)| a + b).collect::<Vec<_>>(), vec![3, 5]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(515);
    for _ in 0..300 {
        let mut l = LinkedList::new();
        let mut model = std::collections::VecDeque::new();
        let mut ops: Vec<String> = Vec::new();
        for _ in 0..12 {
            let x = rng.int(-9, 9) as i32;
            match rng.below(4) {
                0 => {
                    l.push_front(x);
                    model.push_front(x);
                    ops.push(format!("push_front {x}"));
                }
                1 => {
                    l.push_back(x);
                    model.push_back(x);
                    ops.push(format!("push_back {x}"));
                }
                2 => {
                    ops.push("pop_front".into());
                    check!(format!("{ops:?}"), l.pop_front(), model.pop_front());
                }
                _ => {
                    ops.push("pop_back".into());
                    check!(format!("{ops:?}"), l.pop_back(), model.pop_back());
                }
            }
            check!(format!("{ops:?}: contents"), (l.iter().copied().collect::<Vec<_>>(), l.len()), (model.iter().copied().collect::<Vec<_>>(), model.len()));
        }
    }
}

#[test]
fn single_both_ways() {
    let mut l = LinkedList::new();
    check!(r#"push 5; pop_back; push 6; pop_front"#, { l.push_front(5); let a = l.pop_back(); l.push_back(6); (a, l.pop_front(), l.is_empty(), l.iter().count()) }, (Some(5), Some(6), true, 0));
}

#[test]
fn alternating() {
    let mut l = LinkedList::new();
    for i in 0..6 {
        if i % 2 == 0 { l.push_front(i) } else { l.push_back(i) }
    }
    check!(r#"push front/back alternately, 0..6"#, l.iter().copied().collect::<Vec<_>>(), vec![4, 2, 0, 1, 3, 5]);
}

#[test]
fn big_drop() {
    let mut l = LinkedList::new();
    for i in 0..1_000_000 {
        l.push_back(i);
    }
    check!(r#"push 10⁶ then drop"#, l.len(), 1_000_000);
}
