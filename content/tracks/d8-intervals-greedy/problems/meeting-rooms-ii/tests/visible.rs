use solution::*;

#[test]
fn leetcode_two() {
    check!(r#"meetings = [(0, 30), (5, 10), (15, 20)]"#, min_meeting_rooms(&[(0, 30), (5, 10), (15, 20)]), 2);
}

#[test]
fn leetcode_one() {
    check!(r#"meetings = [(7, 10), (2, 4)]"#, min_meeting_rooms(&[(7, 10), (2, 4)]), 1);
}

#[test]
fn no_meetings() {
    check!(r#"meetings = []"#, min_meeting_rooms(&[]), 0);
}

#[test]
fn single() {
    check!(r#"meetings = [(1, 2)]"#, min_meeting_rooms(&[(1, 2)]), 1);
}

#[test]
fn back_to_back_share() {
    check!(r#"meetings = [(1, 5), (5, 10)]"#, min_meeting_rooms(&[(1, 5), (5, 10)]), 1);
}

#[test]
fn all_at_once() {
    check!(r#"meetings = [(1, 5), (1, 5), (1, 5)]"#, min_meeting_rooms(&[(1, 5), (1, 5), (1, 5)]), 3);
}
