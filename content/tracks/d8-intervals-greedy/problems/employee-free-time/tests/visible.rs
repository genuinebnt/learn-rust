use solution::*;

#[test]
fn leetcode_one_gap() {
    check!(r#"schedule = [[(1, 2), (5, 6)], [(1, 3)], [(4, 10)]]"#, employee_free_time(&[vec![(1, 2), (5, 6)], vec![(1, 3)], vec![(4, 10)]]), vec![(3, 4)]);
}

#[test]
fn leetcode_two_gaps() {
    check!(r#"schedule = [[(1, 3), (6, 7)], [(2, 4)], [(2, 5), (9, 12)]]"#, employee_free_time(&[vec![(1, 3), (6, 7)], vec![(2, 4)], vec![(2, 5), (9, 12)]]), vec![(5, 6), (7, 9)]);
}

#[test]
fn no_employees() {
    check!(r#"schedule = []"#, employee_free_time(&[]), Vec::<(i32, i32)>::new());
}

#[test]
fn one_employee() {
    check!(r#"schedule = [[(1, 2), (3, 4)]]"#, employee_free_time(&[vec![(1, 2), (3, 4)]]), vec![(2, 3)]);
}

#[test]
fn touching_is_not_free() {
    check!(r#"schedule = [[(1, 2)], [(2, 3)]]"#, employee_free_time(&[vec![(1, 2)], vec![(2, 3)]]), Vec::<(i32, i32)>::new());
}

#[test]
fn employee_with_no_work() {
    check!(r#"schedule = [[], [(1, 2), (4, 5)]]"#, employee_free_time(&[vec![], vec![(1, 2), (4, 5)]]), vec![(2, 4)]);
}
