use solution::*;

#[test]
fn nothing_fresh() {
    check!(r#"grid = [[0,2]]"#, minutes_to_rot(&[vec![0, 2]]), Some(0));
}

#[test]
fn no_rotten() {
    check!(r#"grid = [[1]]"#, minutes_to_rot(&[vec![1]]), None);
}

#[test]
fn two_sources() {
    check!(r#"grid = [[2,1,1,1,2]]"#, minutes_to_rot(&[vec![2, 1, 1, 1, 2]]), Some(2));
}
