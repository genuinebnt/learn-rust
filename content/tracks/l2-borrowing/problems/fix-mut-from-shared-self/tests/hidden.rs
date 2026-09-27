use solution::*;

#[test]
fn repeated_edits() {
    check!(r#"push 1; add 1 to the top 5 times"#, { let mut s = Stack::new(); s.push(1); for _ in 0..5 { *s.top_mut().unwrap() += 1; } s.items_for_test() }, vec![6]);
}

#[test]
fn to_min() {
    check!(r#"push 0; set top to i32::MIN"#, { let mut s = Stack::new(); s.push(0); *s.top_mut().unwrap() = i32::MIN; s.items_for_test() }, vec![i32::MIN]);
}

#[test]
fn none_then_some() {
    check!(r#"new: None; push 4: Some(4)"#, { let mut s = Stack::new(); let a = s.top_mut().is_none(); s.push(4); (a, s.top_mut().copied()) }, (true, Some(4)));
}

#[test]
fn many_items() {
    check!(r#"push 0..1000; set top to -1"#, { let mut s = Stack::new(); for i in 0..1000 { s.push(i); } *s.top_mut().unwrap() = -1; let v = s.items_for_test(); (v.len(), v[998], v[999]) }, (1000, 998, -1));
}

#[test]
fn duplicates() {
    check!(r#"push 5, 5; set top to 0"#, { let mut s = Stack::new(); s.push(5); s.push(5); *s.top_mut().unwrap() = 0; s.items_for_test() }, vec![5, 0]);
}

#[test]
fn edit_is_seen_by_next_call() {
    check!(r#"push 2; set top to 9; read top"#, { let mut s = Stack::new(); s.push(2); *s.top_mut().unwrap() = 9; s.top_mut().copied() }, Some(9));
}

#[test]
fn max_value() {
    check!(r#"push i32::MAX - 1; add 1"#, { let mut s = Stack::new(); s.push(i32::MAX - 1); *s.top_mut().unwrap() += 1; s.items_for_test() }, vec![i32::MAX]);
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(2003);
    for _ in 0..300 {
        let mut s = Stack::new();
        let mut model: Vec<i32> = Vec::new();
        let mut ops = Vec::new();
        let n = rng.below(12);
        for _ in 0..n {
            if rng.bool() {
                let x = rng.int(-100, 100) as i32;
                s.push(x);
                model.push(x);
                ops.push(format!("push {x}"));
            } else {
                let d = rng.int(-9, 9) as i32;
                if let Some(t) = s.top_mut() {
                    *t += d;
                }
                if let Some(t) = model.last_mut() {
                    *t += d;
                }
                ops.push(format!("top += {d}"));
            }
        }
        check!(ops.join(", "), s.items_for_test(), model);
    }
}
