use solution::*;

#[test]
fn out_of_range() {
    check!(r#"Push 5, Insert(3, 9), Remove(1)"#, apply(&[Op::Push(5), Op::Insert(3, 9), Op::Remove(1)]), vec![5]);
}

#[test]
fn insert_at_end() {
    check!(r#"Push 1, Insert(1, 2), Remove(0)"#, apply(&[Op::Push(1), Op::Insert(1, 2), Op::Remove(0)]), vec![2]);
}

#[test]
fn no_ops() {
    check!(r#"[]"#, apply(&[]), Vec::<i32>::new());
}

#[test]
fn remove_on_empty() {
    check!(r#"Remove(0)"#, apply(&[Op::Remove(0)]), Vec::<i32>::new());
}

#[test]
fn remove_last_index() {
    check!(r#"Push 1, Push 2, Remove(1)"#, apply(&[Op::Push(1), Op::Push(2), Op::Remove(1)]), vec![1]);
}

#[test]
fn insert_middle() {
    check!(r#"Push 1, Push 3, Insert(1, 2)"#, apply(&[Op::Push(1), Op::Push(3), Op::Insert(1, 2)]), vec![1, 2, 3]);
}

#[test]
fn extremes() {
    check!(r#"Push i32::MIN, Push i32::MAX, Insert(0, 0)"#, apply(&[Op::Push(i32::MIN), Op::Push(i32::MAX), Op::Insert(0, 0)]), vec![0, i32::MIN, i32::MAX]);
}

#[test]
fn pop_until_empty_then_more() {
    check!(r#"Push 1, Pop, Pop, Push 2"#, apply(&[Op::Push(1), Op::Pop, Op::Pop, Op::Push(2)]), vec![2]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2301);
    for _ in 0..300 {
        let n = rng.below(12);
        let mut ops = Vec::new();
        let mut want: Vec<i32> = Vec::new();
        for _ in 0..n {
            let x = rng.int(-9, 9) as i32;
            let i = rng.below(5);
            let op = match rng.below(4) {
                0 => Op::Push(x),
                1 => Op::Pop,
                2 => Op::Insert(i, x),
                _ => Op::Remove(i),
            };
            ops.push(op);
            want = match op {
                Op::Push(x) => [&want[..], &[x]].concat(),
                Op::Pop => want[..want.len().saturating_sub(1)].to_vec(),
                Op::Insert(i, x) if i <= want.len() => [&want[..i], &[x], &want[i..]].concat(),
                Op::Remove(i) if i < want.len() => [&want[..i], &want[i + 1..]].concat(),
                _ => want,
            };
        }
        check!(format!("ops = {ops:?}"), apply(&ops), want);
    }
}

#[test]
fn scale_200k() {
    let mut ops: Vec<Op> = (0..200_000).map(Op::Push).collect();
    ops.extend((0..100_000).map(|_| Op::Pop));
    let v = apply(&ops);
    check!("200000 pushes, then 100000 pops", (v.len(), v[99_999]), (100_000, 99_999));
}
