use solution::*;

#[test]
fn possible() {
    check!(r#"n = 2, prereqs = [(0, 1)]"#, can_finish(2, &[(0, 1)]), true);
}

#[test]
fn cycle() {
    check!(r#"n = 2, prereqs = [(0, 1), (1, 0)]"#, can_finish(2, &[(0, 1), (1, 0)]), false);
}
