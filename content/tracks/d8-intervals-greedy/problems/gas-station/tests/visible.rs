use solution::*;

#[test]
fn leetcode_start_three() {
    check!(r#"gas = [1, 2, 3, 4, 5], cost = [3, 4, 5, 1, 2]"#, can_complete_circuit(&[1, 2, 3, 4, 5], &[3, 4, 5, 1, 2]), Some(3));
}

#[test]
fn leetcode_none() {
    check!(r#"gas = [2, 3, 4], cost = [3, 4, 3]"#, can_complete_circuit(&[2, 3, 4], &[3, 4, 3]), None);
}

#[test]
fn single_enough() {
    check!(r#"gas = [5], cost = [4]"#, can_complete_circuit(&[5], &[4]), Some(0));
}

#[test]
fn single_short() {
    check!(r#"gas = [1], cost = [2]"#, can_complete_circuit(&[1], &[2]), None);
}

#[test]
fn exactly_enough() {
    check!(r#"gas = [1, 1], cost = [1, 1]"#, can_complete_circuit(&[1, 1], &[1, 1]), Some(0));
}

#[test]
fn several_work_take_smallest() {
    check!(r#"gas = [1, 0, 2, 0], cost = [0, 1, 0, 2]"#, can_complete_circuit(&[1, 0, 2, 0], &[0, 1, 0, 2]), Some(0));
}
