use solution::*;

#[test]
fn leetcode_clash() {
    check!(r#"meetings = [(0, 30), (5, 10), (15, 20)]"#, can_attend_all(&[(0, 30), (5, 10), (15, 20)]), false);
}

#[test]
fn leetcode_fine() {
    check!(r#"meetings = [(7, 10), (2, 4)]"#, can_attend_all(&[(7, 10), (2, 4)]), true);
}

#[test]
fn no_meetings() {
    check!(r#"meetings = []"#, can_attend_all(&[]), true);
}

#[test]
fn one_meeting() {
    check!(r#"meetings = [(1, 2)]"#, can_attend_all(&[(1, 2)]), true);
}

#[test]
fn back_to_back_is_fine() {
    check!(r#"meetings = [(1, 5), (5, 8)]"#, can_attend_all(&[(1, 5), (5, 8)]), true);
}

#[test]
fn unsorted_overlap() {
    check!(r#"meetings = [(10, 20), (1, 11)]"#, can_attend_all(&[(10, 20), (1, 11)]), false);
}
