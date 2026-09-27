use solution::*;

#[test]
fn chain_of_keys() {
    check!(r#"rooms = [[1],[2],[3],[]]"#, can_visit_all_rooms(&[vec![1], vec![2], vec![3], vec![]]), true);
}

#[test]
fn one_room_stays_locked() {
    check!(r#"rooms = [[1,3],[3,0,1],[2],[0]]"#, can_visit_all_rooms(&[vec![1, 3], vec![3, 0, 1], vec![2], vec![0]]), false);
}

#[test]
fn only_room_zero() {
    check!(r#"rooms = [[]]"#, can_visit_all_rooms(&[vec![]]), true);
}

#[test]
fn key_locked_inside_its_own_room() {
    check!(r#"rooms = [[], [1]]"#, can_visit_all_rooms(&[vec![], vec![1]]), false);
}

#[test]
fn keys_found_later_still_count() {
    check!(r#"rooms = [[2],[],[1]]"#, can_visit_all_rooms(&[vec![2], vec![], vec![1]]), true);
}
