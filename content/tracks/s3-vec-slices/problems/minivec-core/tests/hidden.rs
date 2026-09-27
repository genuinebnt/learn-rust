use solution::*;

use std::rc::Rc;

#[test]
fn drop_releases_every_element() {
    let counter = Rc::new(());
    {
        let mut v = MiniVec::new();
        for _ in 0..10 {
            v.push(Rc::clone(&counter));
        }
        v.pop();
    }
    check!("10 Rc clones pushed, one popped, then the MiniVec dropped", Rc::strong_count(&counter), 1);
}

#[test]
fn many_strings_survive_reallocation() {
    let mut v = MiniVec::new();
    for i in 0..1000 {
        v.push(i.to_string());
    }
    check!("push 0..1000 as Strings", (v.len(), v.get(999).cloned()), (1000, Some("999".to_string())));
}

#[test]
fn pop_empty() {
    check!(r#"new MiniVec"#, MiniVec::<u8>::new().pop(), None);
}

#[test]
fn capacity_sequence() {
    check!(r#"capacity after 1, 4, 5, 8, 9, 16 and 17 pushes"#, { let mut v = MiniVec::new(); let mut caps = vec![]; for i in 1..=17u32 { v.push(i); if [1, 4, 5, 8, 9, 16, 17].contains(&i) { caps.push(v.capacity()); } } caps }, vec![4, 4, 8, 8, 16, 16, 32]);
}

#[test]
fn lifo() {
    check!(r#"push 0..10, then pop everything"#, { let mut v = MiniVec::new(); for i in 0..10 { v.push(i); } let mut out = vec![]; while let Some(x) = v.pop() { out.push(x); } (out, v.len()) }, ((0..10).rev().collect::<Vec<_>>(), 0));
}

#[test]
fn pop_then_push() {
    check!(r#"push 1, 2, pop, push 3"#, { let mut v = MiniVec::new(); v.push(1); v.push(2); v.pop(); v.push(3); (v.len(), v.get(0).copied(), v.get(1).copied()) }, (2, Some(1), Some(3)));
}

#[test]
fn get_after_pop() {
    check!(r#"push 1, pop, get(0)"#, { let mut v = MiniVec::new(); v.push(1); v.pop(); v.get(0).copied() }, None);
}

#[test]
fn drop_releases_a_thousand() {
    let counter = Rc::new(());
    {
        let mut v = MiniVec::new();
        for _ in 0..1000 {
            v.push(Rc::clone(&counter));
        }
        check!("1000 Rc clones inside the MiniVec", Rc::strong_count(&counter), 1001);
    }
    check!("1000 Rc clones pushed, then the MiniVec dropped", Rc::strong_count(&counter), 1);
}

#[test]
fn popped_value_is_owned() {
    let counter = Rc::new(());
    let mut v = MiniVec::new();
    v.push(Rc::clone(&counter));
    let x = v.pop();
    drop(v);
    check!("an Rc popped out, then the MiniVec dropped", Rc::strong_count(&counter), 2);
    drop(x);
}

#[test]
fn random_vs_vec() {
    let mut rng = anneal_prelude::Rng::new(2315);
    for _ in 0..200 {
        let mut ours = MiniVec::new();
        let mut want: Vec<String> = Vec::new();
        let mut ops = Vec::new();
        for _ in 0..rng.below(30) {
            if rng.below(3) == 0 {
                ops.push("pop".to_string());
                check!(format!("{ops:?}"), ours.pop(), want.pop());
            } else {
                let s = rng.below(100).to_string();
                ops.push(format!("push {s}"));
                ours.push(s.clone());
                want.push(s);
            }
        }
        let got: Vec<Option<String>> = (0..want.len() + 1).map(|i| ours.get(i).cloned()).collect();
        let expected: Vec<Option<String>> = want.iter().cloned().map(Some).chain([None]).collect();
        check!(format!("{ops:?}, then get(0..=len)"), (ours.len(), got), (want.len(), expected));
    }
}

#[test]
fn scale_200k() {
    let mut v = MiniVec::new();
    for i in 0..200_000u64 {
        v.push(i);
    }
    let mut sum = 0;
    while let Some(x) = v.pop() {
        sum += x;
    }
    check!("push 0..200000, then pop everything", (sum, v.len(), v.capacity()), (19_999_900_000, 0, 262_144));
}
