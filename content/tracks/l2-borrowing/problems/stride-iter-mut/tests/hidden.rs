use solution::*;

#[test]
fn step_one() {
    check!(r#"[1, 2, 3], step 1"#, { let mut v = [1, 2, 3]; step_mut(&mut v, 1).map(|x| *x).collect::<Vec<_>>() }, vec![1, 2, 3]);
}

#[test]
fn step_larger_than_len() {
    check!(r#"[5, 6], step 10"#, { let mut v = [5, 6]; step_mut(&mut v, 10).map(|x| *x).collect::<Vec<_>>() }, vec![5]);
}

#[test]
fn both_ends_meet() {
    check!(r#"[0..9], step 2: next, next_back, next, next_back, next, next"#, { let mut v = [0, 1, 2, 3, 4, 5, 6, 7, 8]; let mut it = step_mut(&mut v, 2); let a = [it.next().copied(), it.next_back().copied(), it.next().copied(), it.next_back().copied(), it.next().copied(), it.next().copied()]; a }, [Some(0), Some(8), Some(2), Some(6), Some(4), None]);
}

#[test]
fn len_after_next_back() {
    check!(r#"[0..10], step 3: next_back then len"#, { let mut v = [0; 10]; let mut it = step_mut(&mut v, 3); it.next_back(); it.len() }, 3);
}

#[test]
fn len_after_next() {
    check!(r#"[0..10], step 3: next then len"#, { let mut v = [0; 10]; let mut it = step_mut(&mut v, 3); it.next(); it.len() }, 3);
}

#[test]
fn strings() {
    check!(r#"["a", "b", "c"], step 2: push '!'"#, { let mut v = ["a", "b", "c"].map(String::from); for s in step_mut(&mut v, 2) { s.push('!'); } v }, ["a!", "b", "c!"].map(String::from));
}

#[test]
fn single() {
    check!(r#"[9], step 1: next_back, then next"#, { let mut v = [9]; let mut it = step_mut(&mut v, 1); (it.next_back().copied(), it.next().is_none()) }, (Some(9), true));
}

#[test]
fn zip_two_iterators() {
    check!(r#"swap v[0,2,4] with v[1,3,5] via split_at_mut halves"#, { let mut v = [1, 2, 3, 4, 5, 6]; let (a, b) = v.split_at_mut(3); for (x, y) in step_mut(a, 1).zip(step_mut(b, 1)) { std::mem::swap(x, y); } v }, [4, 5, 6, 1, 2, 3]);
}

#[test]
fn step_zero_panics() {
    let mut v = [1, 2];
    let r = std::panic::catch_unwind(move || step_mut(&mut v, 0).count());
    check!("step_mut(.., 0) panics", r.is_err(), true);
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6217);
    for _ in 0..400 {
        let n = rng.below(12);
        let step = 1 + rng.below(5);
        let v: Vec<i32> = (0..n as i32).collect();
        let mut left: Vec<i32> = v.iter().copied().step_by(step).collect();
        let mut got_v = v.clone();
        let mut it = step_mut(&mut got_v, step);
        let mut ops = Vec::new();
        for _ in 0..6 {
            let back = rng.bool();
            let want = if back { left.pop() } else if left.is_empty() { None } else { Some(left.remove(0)) };
            let got = if back { it.next_back() } else { it.next() };
            ops.push(if back { "next_back" } else { "next" });
            let got = got.map(|x| {
                let seen = *x;
                *x = -1;
                seen
            });
            check!(format!("0..{n}, step {step}: {}", ops.join(", ")), (got, it.len()), (want, left.len()));
        }
    }
}

#[test]
fn big_slice() {
    let mut v: Vec<u32> = (0..1_000_000).collect();
    for x in step_mut(&mut v, 1000) {
        *x = 7;
    }
    let n = step_mut(&mut v, 3).len();
    check!("1000000 elements: step 1000 writes, then len at step 3", (n, v[999_000], v[999_001]), (333_334, 7, 999_001));
}
