use solution::*;

#[test]
fn one_wall() {
    check!(r#"grid = [".#.", ".#.", ".#."]"#, min_walls(&[".#.", ".#.", ".#."]), 1);
}

#[test]
fn open() {
    check!(r#"grid = ["..", ".."]"#, min_walls(&["..", ".."]), 0);
}
