use solution::*;

#[test]
fn both() {
    check!(r#"v = [1, 2, 3], i = 0, j = 2"#, { let mut v = [1, 2, 3]; if let Some((a, b)) = pair_mut(&mut v, 0, 2) { std::mem::swap(a, b); } v }, [3, 2, 1]);
}

#[test]
fn same_index() {
    check!(r#"i = j = 1"#, pair_mut(&mut [1, 2], 1, 1).is_none(), true);
}

#[test]
fn adjacent() {
    check!(r#"v = [1, 2], i = 0, j = 1"#, { let mut v = [1, 2]; if let Some((a, b)) = pair_mut(&mut v, 0, 1) { std::mem::swap(a, b); } v }, [2, 1]);
}

#[test]
fn order_kept() {
    check!(r#"i = 2, j = 0"#, { let mut v = [10, 20, 30]; let (a, b) = pair_mut(&mut v, 2, 0).unwrap(); (*a, *b) }, (30, 10));
}

#[test]
fn i_out_of_bounds() {
    check!(r#"v = [1, 2], i = 2, j = 0"#, pair_mut(&mut [1, 2], 2, 0).is_none(), true);
}
