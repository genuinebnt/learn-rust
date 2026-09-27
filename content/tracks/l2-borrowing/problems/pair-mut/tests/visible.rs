use solution::*;

#[test]
fn both() {
    check!(r#"v = [1, 2, 3], i = 0, j = 2"#, { let mut v = [1, 2, 3]; if let Some((a, b)) = pair_mut(&mut v, 0, 2) { std::mem::swap(a, b); } v }, [3, 2, 1]);
}

#[test]
fn same_index() {
    check!(r#"i = j = 1"#, pair_mut(&mut [1, 2], 1, 1).is_none(), true);
}
