use solution::*;

#[test]
fn leetcode_three() {
    check!(r#"courses = [(100, 200), (200, 1300), (1000, 1250), (2000, 3200)]"#, schedule_course(&[(100, 200), (200, 1300), (1000, 1250), (2000, 3200)]), 3);
}

#[test]
fn leetcode_one() {
    check!(r#"courses = [(1, 2)]"#, schedule_course(&[(1, 2)]), 1);
}

#[test]
fn leetcode_none_fit() {
    check!(r#"courses = [(3, 2), (4, 3)]"#, schedule_course(&[(3, 2), (4, 3)]), 0);
}

#[test]
fn no_courses() {
    check!(r#"courses = []"#, schedule_course(&[]), 0);
}

#[test]
fn finish_on_the_last_day() {
    check!(r#"courses = [(5, 5)]"#, schedule_course(&[(5, 5)]), 1);
}

#[test]
fn swap_long_for_short() {
    check!(r#"courses = [(4, 4), (1, 5), (1, 5), (1, 5)]"#, schedule_course(&[(4, 4), (1, 5), (1, 5), (1, 5)]), 3);
}
