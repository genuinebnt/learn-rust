use solution::*;

#[test]
fn one_wall() {
    check!(r#"grid = [".#.", ".#.", ".#."]"#, min_walls(&[".#.", ".#.", ".#."]), 1);
}

#[test]
fn open() {
    check!(r#"grid = ["..", ".."]"#, min_walls(&["..", ".."]), 0);
}

#[test]
fn single_cell() {
    check!(r#"grid = ["."]"#, min_walls(&["."]), 0);
}

#[test]
fn two_walls_in_a_row() {
    check!(r##"grid = [".", "#", "#", "."]"##, min_walls(&[".", "#", "#", "."]), 2);
}

#[test]
fn walk_around_for_free() {
    check!(r###"grid = ["...", "##.", "..."]"###, min_walls(&["...", "##.", "..."]), 0);
}
