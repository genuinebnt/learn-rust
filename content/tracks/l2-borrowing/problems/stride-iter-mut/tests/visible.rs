use solution::*;

#[test]
fn every_other() {
    check!(r#"[1, 2, 3, 4, 5], step 2; add 10 to each"#, { let mut v = [1, 2, 3, 4, 5]; for x in step_mut(&mut v, 2) { *x += 10; } v }, [11, 2, 13, 4, 15]);
}

#[test]
fn items_live_together() {
    check!(r#"[1, 2, 3, 4], step 3; collect, then write through each"#, { let mut v = [1, 2, 3, 4]; let refs: Vec<&mut i32> = step_mut(&mut v, 3).collect(); for r in refs { *r = 0; } v }, [0, 2, 3, 0]);
}

#[test]
fn len_is_exact() {
    check!(r#"len of step_mut on 7 elements, steps 1, 2, 3, 7, 8"#, { let mut v = [0; 7]; (step_mut(&mut v, 1).len(), step_mut(&mut v, 2).len(), step_mut(&mut v, 3).len(), step_mut(&mut v, 7).len(), step_mut(&mut v, 8).len()) }, (7, 4, 3, 1, 1));
}

#[test]
fn reversed() {
    check!(r#"[0, 1, 2, 3, 4, 5, 6], step 3, reversed"#, { let mut v = [0, 1, 2, 3, 4, 5, 6]; step_mut(&mut v, 3).rev().map(|x| *x).collect::<Vec<_>>() }, vec![6, 3, 0]);
}

#[test]
fn back_when_unaligned() {
    check!(r#"[0, 1, 2, 3, 4, 5], step 4: next_back"#, { let mut v = [0, 1, 2, 3, 4, 5]; step_mut(&mut v, 4).next_back().copied() }, Some(4));
}

#[test]
fn empty() {
    check!(r#"[], step 2"#, { let mut v: [i32; 0] = []; let mut it = step_mut(&mut v, 2); (it.len(), it.next().is_none(), it.next_back().is_none()) }, (0, true, true));
}
