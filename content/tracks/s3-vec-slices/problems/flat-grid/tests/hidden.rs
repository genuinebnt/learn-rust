use solution::*;

#[test]
fn empty_grid() {
    check!(r#"0×0 grid"#, { let g = Grid::new(0, 0); (g.get(0, 0), g.row(0).is_none()) }, (None, true));
}

#[test]
fn x_not_wrapping() {
    check!(r#"2×2 grid, get (2, 0)"#, { let mut g = Grid::new(2, 2); g.set(0, 1, 9); g.get(2, 0) }, None);
}
