use solution::*;

fn run(rows: &[&str]) -> Vec<String> {
    let mut board: Vec<Vec<char>> = rows.iter().map(|r| r.chars().collect()).collect();
    capture_regions(&mut board);
    board.iter().map(|r| r.iter().collect()).collect()
}

#[test]
fn classic() {
    check!(r#"board = ["XXXX", "XOOX", "XXOX", "XOXX"]"#, run(&["XXXX", "XOOX", "XXOX", "XOXX"]), vec!["XXXX", "XXXX", "XXXX", "XOXX"]);
}

#[test]
fn single_x() {
    check!(r#"board = ["X"]"#, run(&["X"]), vec!["X"]);
}

#[test]
fn border_o_stays() {
    check!(r#"board = ["O"]"#, run(&["O"]), vec!["O"]);
}

#[test]
fn escapes_through_a_chain() {
    check!(r#"board = ["XXXX", "XOOO", "XOXX", "XXXX"]"#, run(&["XXXX", "XOOO", "XOXX", "XXXX"]), vec!["XXXX", "XOOO", "XOXX", "XXXX"]);
}

#[test]
fn diagonal_is_not_an_escape() {
    check!(r#"board = ["XXX", "XOX", "XXO"]"#, run(&["XXX", "XOX", "XXO"]), vec!["XXX", "XXX", "XXO"]);
}
