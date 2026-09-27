use solution::*;

#[test]
fn leetcode_four() {
    check!(r#"envelopes = [(5, 4), (6, 4), (6, 7), (2, 3)]"#, max_envelopes(&[(5, 4), (6, 4), (6, 7), (2, 3)]), 3);
}

#[test]
fn leetcode_all_same() {
    check!(r#"envelopes = [(1, 1), (1, 1), (1, 1)]"#, max_envelopes(&[(1, 1), (1, 1), (1, 1)]), 1);
}

#[test]
fn empty() {
    check!(r#"envelopes = []"#, max_envelopes(&[]), 0);
}

#[test]
fn single() {
    check!(r#"envelopes = [(1, 1)]"#, max_envelopes(&[(1, 1)]), 1);
}

#[test]
fn same_width_never_nests() {
    check!(r#"envelopes = [(2, 3), (2, 4)]"#, max_envelopes(&[(2, 3), (2, 4)]), 1);
}

#[test]
fn no_rotation() {
    check!(r#"envelopes = [(3, 1), (2, 2), (1, 3)]"#, max_envelopes(&[(3, 1), (2, 2), (1, 3)]), 1);
}
