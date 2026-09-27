use solution::*;

/// No derives: not Default, Clone or Copy.
struct Token(u32);

#[test]
fn capacity_is_a_const() {
    const CAP: usize = Ring::<u8, 4>::CAPACITY;
    check!(r#"const CAP: usize = Ring::<u8, 4>::CAPACITY"#, CAP, 4);
}

#[test]
fn empty_ring() {
    let r: Ring<i32, 3> = Ring::new();
    check!(r#"Ring<i32, 3>::new()"#, (r.len(), r.iter().count()), (0, 0));
}

#[test]
fn wraps_many_times() {
    let mut r: Ring<u32, 3> = Ring::new();
    for i in 0..10 {
        r.push(i);
    }
    check!(r#"Ring<u32, 3>: push 0..10"#, (r.len(), r.iter().copied().collect::<Vec<_>>()), (3, vec![7, 8, 9]));
}

#[test]
fn zero_capacity_tokens() {
    let mut r: Ring<Token, 0> = Ring::new();
    check!(r#"Ring<Token, 0>: push Token(9)"#, r.push(Token(9)).map(|t| t.0), Some(9));
}

#[test]
fn capacity_one() {
    let mut r: Ring<char, 1> = Ring::new();
    check!(r#"Ring<char, 1>: push a, b"#, (r.push('a'), r.push('b'), r.iter().copied().collect::<String>()), (None, Some('a'), "b".to_string()));
}

#[test]
fn concat_empty() {
    let c: [u8; 0] = concat([], []);
    check!(r#"concat([], []) as [u8; 0]"#, c.len(), 0);
}

#[test]
fn concat_turbofish() {
    check!(r#"concat::<char, 1, 2, 3>(['a'], ['b', 'c'])"#, concat::<char, 1, 2, 3>(['a'], ['b', 'c']), ['a', 'b', 'c']);
}

#[test]
fn concat_tokens() {
    let c: [Token; 2] = concat([Token(1)], [Token(2)]);
    check!(r#"concat([Token(1)], [Token(2)])"#, c.map(|t| t.0), [1, 2]);
}

#[test]
fn drops_evicted_and_remaining() {
    let rc = std::rc::Rc::new(0);
    let mut r: Ring<std::rc::Rc<i32>, 2> = Ring::new();
    for _ in 0..5 {
        r.push(rc.clone());
    }
    drop(r);
    check!(r#"Rc clones through a Ring<Rc<i32>, 2>, then drop it"#, std::rc::Rc::strong_count(&rc), 1);
}

#[test]
fn random_vs_vecdeque() {
    let mut rng = anneal_prelude::Rng::new(4510);
    for _ in 0..300 {
        let mut r: Ring<i64, 4> = Ring::new();
        let mut model = std::collections::VecDeque::new();
        let n = rng.below(12);
        let xs: Vec<i64> = rng.vec(n, -9, 9);
        for &x in &xs {
            let want = if model.len() == 4 { model.pop_front() } else { None };
            model.push_back(x);
            check!(format!("push {xs:?} into Ring<_, 4>"), r.push(x), want);
        }
        check!(format!("push {xs:?} into Ring<_, 4>"), (r.len(), r.iter().copied().collect::<Vec<_>>()), (model.len(), model.iter().copied().collect::<Vec<_>>()));
    }
}

#[test]
fn random_concat() {
    let mut rng = anneal_prelude::Rng::new(4511);
    for _ in 0..200 {
        let a: [i32; 3] = [rng.int(-9, 9) as i32, rng.int(-9, 9) as i32, rng.int(-9, 9) as i32];
        let b: [i32; 2] = [rng.int(-9, 9) as i32, rng.int(-9, 9) as i32];
        let c: [i32; 5] = concat(a, b);
        check!(format!("concat({a:?}, {b:?})"), c.to_vec(), [a.to_vec(), b.to_vec()].concat());
    }
}
