use solution::*;

#[test]
fn possible() {
    check!(r#"n = 2, prereqs = [(0, 1)]"#, can_finish(2, &[(0, 1)]), true);
}

#[test]
fn cycle() {
    check!(r#"n = 2, prereqs = [(0, 1), (1, 0)]"#, can_finish(2, &[(0, 1), (1, 0)]), false);
}

#[test]
fn no_prereqs() {
    check!(r#"n = 3, prereqs = []"#, can_finish(3, &[]), true);
}

#[test]
fn diamond_is_not_a_cycle() {
    check!(r#"n = 4, prereqs = [(0, 1), (0, 2), (1, 3), (2, 3)]"#, can_finish(4, &[(0, 1), (0, 2), (1, 3), (2, 3)]), true);
}

#[test]
fn cycle_after_a_free_course() {
    check!(r#"n = 3, prereqs = [(0, 1), (1, 2), (2, 1)]"#, can_finish(3, &[(0, 1), (1, 2), (2, 1)]), false);
}
