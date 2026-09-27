use solution::*;

#[test]
fn get_past_len() {
    check!(r#"push 1 item"#, { let mut v = SmallVec4::new(); v.push('a'); (v.get(1).copied(), v.get(0).copied()) }, (None, Some('a')));
}

#[test]
fn strings() {
    check!(r#"push 6 Strings"#, { let mut v = SmallVec4::new(); for w in ["a", "b", "c", "d", "e", "f"] { v.push(w.to_string()); } v.get(5).cloned() }, Some("f".to_string()));
}

#[test]
fn three_inline() {
    check!(r#"push 3 items"#, { let mut v = SmallVec4::new(); for i in 0..3 { v.push(i); } (v.len(), v.is_inline(), v.get(3).copied()) }, (3, true, None));
}

#[test]
fn hundred() {
    check!(r#"push 0..100"#, { let mut v = SmallVec4::new(); for i in 0..100 { v.push(i); } (v.len(), v.is_inline(), v.get(99).copied(), v.get(100).copied()) }, (100, false, Some(99), None));
}

#[test]
fn spilled_keeps_first_four() {
    check!(r#"push 5 Strings"#, { let mut v = SmallVec4::new(); for w in ["a", "b", "c", "d", "e"] { v.push(w.to_string()); } (0..5).map(|i| v.get(i).cloned().unwrap_or_default()).collect::<String>() }, "abcde".to_string());
}

#[test]
fn get_past_len_inline() {
    check!(r#"push 4 items, get(4)"#, { let mut v = SmallVec4::new(); for i in 0..4 { v.push(i); } (v.get(4).copied(), v.is_inline()) }, (None, true));
}

use std::rc::Rc;

#[test]
fn nothing_leaks_after_spill() {
    let counter = Rc::new(());
    {
        let mut v = SmallVec4::new();
        for _ in 0..6 {
            v.push(Rc::clone(&counter));
        }
        check!("6 Rc clones inside", Rc::strong_count(&counter), 7);
    }
    check!("6 Rc clones pushed, then the SmallVec4 dropped", Rc::strong_count(&counter), 1);
}

#[test]
fn random_vs_vec() {
    let mut rng = anneal_prelude::Rng::new(2317);
    for _ in 0..200 {
        let n = rng.below(12);
        let values: Vec<i32> = rng.vec(n, -50, 50);
        let mut v = SmallVec4::new();
        for &x in &values {
            v.push(x);
        }
        let got: Vec<Option<i32>> = (0..n + 1).map(|i| v.get(i).copied()).collect();
        let want: Vec<Option<i32>> = values.iter().copied().map(Some).chain([None]).collect();
        check!(format!("push {values:?}"), (v.len(), v.is_inline(), got), (n, n <= 4, want));
    }
}

#[test]
fn scale_200k() {
    let mut v = SmallVec4::new();
    for i in 0..200_000u32 {
        v.push(i);
    }
    check!("push 0..200000", (v.len(), v.get(3).copied(), v.get(199_999).copied()), (200_000, Some(3), Some(199_999)));
}
