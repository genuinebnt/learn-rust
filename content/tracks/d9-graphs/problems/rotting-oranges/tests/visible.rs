use solution::*;

#[test]
fn four() {
    check!(r#"grid = [[2,1,1],[1,1,0],[0,1,1]]"#, minutes_to_rot(&[vec![2, 1, 1], vec![1, 1, 0], vec![0, 1, 1]]), Some(4));
}

#[test]
fn stranded() {
    check!(r#"grid = [[2,1,1],[0,1,1],[1,0,1]]"#, minutes_to_rot(&[vec![2, 1, 1], vec![0, 1, 1], vec![1, 0, 1]]), None);
}

#[test]
fn no_fresh_is_zero_minutes() {
    check!(r#"grid = [[0,2]]"#, minutes_to_rot(&[vec![0, 2]]), Some(0));
}

#[test]
fn diagonal_does_not_spread() {
    check!(r#"grid = [[2,0],[0,1]]"#, minutes_to_rot(&[vec![2, 0], vec![0, 1]]), None);
}

#[test]
fn all_sources_spread_at_once() {
    check!(r#"grid = [[2,1,1],[1,1,1],[1,1,2]]"#, minutes_to_rot(&[vec![2, 1, 1], vec![1, 1, 1], vec![1, 1, 2]]), Some(2));
}
