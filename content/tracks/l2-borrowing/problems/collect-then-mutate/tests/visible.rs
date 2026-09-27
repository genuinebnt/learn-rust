use solution::*;

#[test]
fn blinker() {
    check!(r#"5x5, alive [(1, 2), (2, 2), (3, 2)], 1 steps"#, { let mut l = Life::new(5, 5, &[(1, 2), (2, 2), (3, 2)]); for _ in 0..1 { l.step(); } l.alive() }, vec![(2, 1), (2, 2), (2, 3)]);
}

#[test]
fn blinker_twice() {
    check!(r#"5x5, alive [(1, 2), (2, 2), (3, 2)], 2 steps"#, { let mut l = Life::new(5, 5, &[(1, 2), (2, 2), (3, 2)]); for _ in 0..2 { l.step(); } l.alive() }, vec![(1, 2), (2, 2), (3, 2)]);
}

#[test]
fn block_is_still() {
    check!(r#"4x4, alive [(1, 1), (2, 1), (1, 2), (2, 2)], 3 steps"#, { let mut l = Life::new(4, 4, &[(1, 1), (2, 1), (1, 2), (2, 2)]); for _ in 0..3 { l.step(); } l.alive() }, vec![(1, 1), (2, 1), (1, 2), (2, 2)]);
}

#[test]
fn lonely_cell_dies() {
    check!(r#"3x3, alive [(1, 1)], 1 steps"#, { let mut l = Life::new(3, 3, &[(1, 1)]); for _ in 0..1 { l.step(); } l.alive() }, vec![]);
}

#[test]
fn edges_are_dead() {
    check!(r#"3x1, alive [(0, 0), (1, 0), (2, 0)], 1 steps"#, { let mut l = Life::new(3, 1, &[(0, 0), (1, 0), (2, 0)]); for _ in 0..1 { l.step(); } l.alive() }, vec![(1, 0)]);
}

#[test]
fn glider() {
    check!(r#"6x6, alive [(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)], 4 steps"#, { let mut l = Life::new(6, 6, &[(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)]); for _ in 0..4 { l.step(); } l.alive() }, vec![(2, 1), (3, 2), (1, 3), (2, 3), (3, 3)]);
}
