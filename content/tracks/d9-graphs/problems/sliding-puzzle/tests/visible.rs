use solution::*;

#[test]
fn one_move() {
    check!(r#"board = [[1,2,3],[4,0,5]]"#, sliding_puzzle([[1, 2, 3], [4, 0, 5]]), Some(1));
}

#[test]
fn unsolvable() {
    check!(r#"board = [[1,2,3],[5,4,0]]"#, sliding_puzzle([[1, 2, 3], [5, 4, 0]]), None);
}

#[test]
fn five_moves() {
    check!(r#"board = [[4,1,2],[5,0,3]]"#, sliding_puzzle([[4, 1, 2], [5, 0, 3]]), Some(5));
}

#[test]
fn already_solved() {
    check!(r#"board = [[1,2,3],[4,5,0]]"#, sliding_puzzle([[1, 2, 3], [4, 5, 0]]), Some(0));
}

#[test]
fn fourteen_moves() {
    check!(r#"board = [[3,2,4],[1,5,0]]"#, sliding_puzzle([[3, 2, 4], [1, 5, 0]]), Some(14));
}
