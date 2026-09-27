use solution::*;

#[test]
fn empty_grid() {
    check!(r#"0×0 grid"#, { let g = Grid::new(0, 0); (g.get(0, 0), g.row(0).is_none()) }, (None, true));
}

#[test]
fn x_not_wrapping() {
    check!(r#"2×2 grid, get (2, 0)"#, { let mut g = Grid::new(2, 2); g.set(0, 1, 9); g.get(2, 0) }, None);
}

#[test]
fn one_by_one() {
    check!(r#"1×1 grid"#, { let mut g = Grid::new(1, 1); (g.set(0, 0, 3), g.get(0, 0), g.row(0).map(|r| r.to_vec())) }, (true, Some(3), Some(vec![3])));
}

#[test]
fn wide() {
    check!(r#"5×1 grid, set (4, 0) = 9"#, { let mut g = Grid::new(5, 1); g.set(4, 0, 9); g.row(0).map(|r| r.to_vec()) }, Some(vec![0, 0, 0, 0, 9]));
}

#[test]
fn tall() {
    check!(r#"1×5 grid, set (0, 4) = 9"#, { let mut g = Grid::new(1, 5); g.set(0, 4, 9); (g.row(4).map(|r| r.to_vec()), g.get(0, 3)) }, (Some(vec![9]), Some(0)));
}

#[test]
fn row_major_not_column_major() {
    check!(r#"3×2 grid, set (2, 0) = 5"#, { let mut g = Grid::new(3, 2); g.set(2, 0, 5); (g.row(0).map(|r| r.to_vec()), g.row(1).map(|r| r.to_vec())) }, (Some(vec![0, 0, 5]), Some(vec![0, 0, 0])));
}

#[test]
fn overwrite() {
    check!(r#"2×2 grid, set (1, 1) = 1 then 2"#, { let mut g = Grid::new(2, 2); g.set(1, 1, 1); g.set(1, 1, 2); g.get(1, 1) }, Some(2));
}

#[test]
fn huge_coordinates() {
    check!(r#"2×2 grid, x or y = usize::MAX"#, { let mut g = Grid::new(2, 2); (g.get(usize::MAX, 0), g.get(0, usize::MAX), g.set(usize::MAX, 1, 1), g.row(usize::MAX).is_none()) }, (None, None, false, true));
}

#[test]
fn zero_width_rows() {
    check!(r#"0×3 grid"#, { let g = Grid::new(0, 3); (g.get(0, 0), g.row(2).map(|r| r.len())) }, (None, Some(0)));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(2313);
    for _ in 0..200 {
        let (w, h) = (rng.below(5), rng.below(5));
        let mut g = Grid::new(w, h);
        let mut model = vec![vec![0u8; w]; h];
        let mut ops = Vec::new();
        for _ in 0..10 {
            let (x, y, value) = (rng.below(6), rng.below(6), rng.below(256) as u8);
            ops.push((x, y, value));
            let ok = x < w && y < h;
            if ok {
                model[y][x] = value;
            }
            check!(format!("{w}×{h} grid, sets {ops:?}"), g.set(x, y, value), ok);
        }
        for y in 0..6 {
            for x in 0..6 {
                let want = if x < w && y < h { Some(model[y][x]) } else { None };
                check!(format!("{w}×{h} grid, sets {ops:?}, get({x}, {y})"), g.get(x, y), want);
            }
            check!(format!("{w}×{h} grid, sets {ops:?}, row({y})"), g.row(y).map(|r| r.to_vec()), model.get(y).cloned());
        }
    }
}

#[test]
fn big_grid() {
    let mut g = Grid::new(1000, 1000);
    g.set(999, 0, 1);
    g.set(0, 999, 2);
    g.set(999, 999, 3);
    check!("1000×1000 grid, corners set", (g.get(999, 0), g.get(0, 999), g.row(999).map(|r| r[999]), g.get(1000, 999)), (Some(1), Some(2), Some(3), None));
}
