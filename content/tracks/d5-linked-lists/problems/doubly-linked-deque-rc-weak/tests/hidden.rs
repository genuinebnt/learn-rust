use solution::*;

#[test]
fn single_both_ways() {
    let mut d = Deque::new();
    check!(r#"push 7; pop_back; then push 8; pop_front"#, { d.push_back(7); let a = d.pop_back(); d.push_front(8); (a, d.pop_front(), d.is_empty()) }, (Some(7), Some(8), true));
}

#[test]
fn reuse_after_empty() {
    let mut d = Deque::new();
    check!(r#"push_front 1; pop_front; push_back 2, 3; pop_back"#, { d.push_front(1); d.pop_front(); d.push_back(2); d.push_back(3); (d.pop_back(), d.front(), d.back(), d.len()) }, (Some(3), Some(2), Some(2), 1));
}

#[test]
fn pop_front_to_empty_then_back() {
    let mut d = Deque::new();
    d.push_back(1);
    d.push_back(2);
    check!(r#"push_back 1,2; pop_front twice; pop_back"#, (d.pop_front(), d.pop_front(), d.pop_back(), d.back()), (Some(1), Some(2), None, None));
}

#[test]
fn extremes() {
    let mut d = Deque::new();
    d.push_front(i32::MIN);
    d.push_back(i32::MAX);
    check!(r#"push i32::MIN front, i32::MAX back"#, (d.pop_back(), d.pop_back()), (Some(i32::MAX), Some(i32::MIN)));
}

#[test]
fn drain_from_front_pushed_front() {
    let mut d = Deque::new();
    for i in 0..5 {
        d.push_front(i);
    }
    let out: Vec<i32> = std::iter::from_fn(|| d.pop_front()).collect();
    check!(r#"push_front 0..5; pop_front until empty"#, out, vec![4, 3, 2, 1, 0]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(514);
    for _ in 0..300 {
        let mut d = Deque::new();
        let mut model = std::collections::VecDeque::new();
        let mut ops: Vec<String> = Vec::new();
        for _ in 0..12 {
            let x = rng.int(-9, 9) as i32;
            match rng.below(4) {
                0 => {
                    d.push_front(x);
                    model.push_front(x);
                    ops.push(format!("push_front {x}"));
                }
                1 => {
                    d.push_back(x);
                    model.push_back(x);
                    ops.push(format!("push_back {x}"));
                }
                2 => {
                    ops.push("pop_front".into());
                    check!(format!("{ops:?}"), d.pop_front(), model.pop_front());
                }
                _ => {
                    ops.push("pop_back".into());
                    check!(format!("{ops:?}"), d.pop_back(), model.pop_back());
                }
            }
            check!(format!("{ops:?}: front, back, len"), (d.front(), d.back(), d.len(), d.is_empty()), (model.front().copied(), model.back().copied(), model.len(), model.is_empty()));
        }
    }
}

#[test]
fn drain_from_back() {
    let mut d = Deque::new();
    for i in 0..5 {
        d.push_back(i);
    }
    let out: Vec<i32> = std::iter::from_fn(|| d.pop_back()).collect();
    check!(r#"push_back 0..5; pop_back until empty"#, out, vec![4, 3, 2, 1, 0]);
}

#[test]
fn big_drop() {
    let mut d = Deque::new();
    for i in 0..1_000_000 {
        d.push_back(i);
    }
    check!(r#"push 10⁶ then drop"#, d.len(), 1_000_000);
}
