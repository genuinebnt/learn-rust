use solution::*;

#[test]
fn run() {
    check!(r#"[5,7,7,8,8,10], 8"#, search_range(&[5, 7, 7, 8, 8, 10], 8), Some((3, 4)));
}

#[test]
fn missing() {
    check!(r#"[5,7,7,8,8,10], 6"#, search_range(&[5, 7, 7, 8, 8, 10], 6), None);
}

#[test]
fn empty_slice() {
    check!(r#"[], 0"#, search_range(&[], 0), None);
}

#[test]
fn single_match() {
    check!(r#"[1], 1"#, search_range(&[1], 1), Some((0, 0)));
}

#[test]
fn run_at_the_end() {
    check!(r#"[1,2,2], 2"#, search_range(&[1, 2, 2], 2), Some((1, 2)));
}
