use solution::*;

#[test]
fn push_then_pop() {
    let mut l = list(&[1]);
    check!(r#"push 5 onto [1]; pop"#, { push_front(&mut l, 5); (pop_front(&mut l), values(&l)) }, (Some(5), vec![1]));
}

#[test]
fn drain() {
    let mut l = list(&[4, 5]);
    check!(r#"[4,5]; pop three times"#, (pop_front(&mut l), pop_front(&mut l), pop_front(&mut l), l), (Some(4), Some(5), None, None));
}

#[test]
fn push_onto_empty() {
    let mut l = None;
    check!(r#"push 3 onto []; pop"#, { push_front(&mut l, 3); (pop_front(&mut l), l) }, (Some(3), None));
}

#[test]
fn rest_kept() {
    let mut l = list(&[1, 2, 3, 4]);
    check!(r#"[1,2,3,4]; pop once"#, (pop_front(&mut l), values(&l)), (Some(1), vec![2, 3, 4]));
}

#[test]
fn extremes() {
    let mut l = list(&[i32::MIN, i32::MAX]);
    check!(r#"[i32::MIN, i32::MAX]; pop twice"#, (pop_front(&mut l), pop_front(&mut l)), (Some(i32::MIN), Some(i32::MAX)));
}

#[test]
fn stack_order() {
    let mut l = None;
    check!(r#"push 1, 2, 3; pop three"#, { for x in 1..=3 { push_front(&mut l, x); } (pop_front(&mut l), pop_front(&mut l), pop_front(&mut l)) }, (Some(3), Some(2), Some(1)));
}

#[test]
fn pop_empty_twice() {
    let mut l: Option<Box<ListNode>> = None;
    check!(r#"[]; pop twice"#, (pop_front(&mut l), pop_front(&mut l)), (None, None));
}

#[test]
fn drain_10k() {
    let mut l = list(&(0..10_000).collect::<Vec<i32>>());
    check!(r#"10⁴ nodes; pop all"#, { let mut sum = 0i64; while let Some(v) = pop_front(&mut l) { sum += v as i64; } (sum, l) }, (49_995_000, None));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(505);
    for _ in 0..300 {
        let mut l = None;
        let mut model: Vec<i32> = Vec::new();
        let mut ops = Vec::new();
        for _ in 0..8 {
            if rng.bool() {
                let x = rng.int(-9, 9) as i32;
                push_front(&mut l, x);
                model.insert(0, x);
                ops.push(format!("push {x}"));
            } else {
                let want = if model.is_empty() { None } else { Some(model.remove(0)) };
                ops.push("pop".to_string());
                check!(format!("{ops:?}"), pop_front(&mut l), want);
            }
            check!(format!("{ops:?}: list"), values(&l), model.clone());
        }
    }
}
