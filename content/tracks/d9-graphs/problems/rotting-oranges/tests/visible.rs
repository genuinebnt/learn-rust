use solution::*;

#[test]
fn four() {
    check!(r#"grid = [[2,1,1],[1,1,0],[0,1,1]]"#, minutes_to_rot(&[vec![2, 1, 1], vec![1, 1, 0], vec![0, 1, 1]]), Some(4));
}

#[test]
fn stranded() {
    check!(r#"grid = [[2,1,1],[0,1,1],[1,0,1]]"#, minutes_to_rot(&[vec![2, 1, 1], vec![0, 1, 1], vec![1, 0, 1]]), None);
}
