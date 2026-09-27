use solution::*;

#[test]
fn set_and_get() {
    check!(r#"3×2 grid, set (2, 1) = 7"#, { let mut g = Grid::new(3, 2); g.set(2, 1, 7); (g.get(2, 1), g.get(0, 0)) }, (Some(7), Some(0)));
}

#[test]
fn row() {
    let mut g = Grid::new(3, 2);
    g.set(1, 1, 5);
    check!(r#"3×2 grid, set (1, 1) = 5"#, g.row(1), Some(&[0, 5, 0][..]));
}

#[test]
fn out_of_bounds() {
    check!(r#"3×2 grid"#, { let mut g = Grid::new(3, 2); (g.get(3, 0), g.set(0, 2, 1), g.row(2).is_none()) }, (None, false, true));
}
