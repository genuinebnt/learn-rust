use solution::*;

#[test]
fn negative() {
    check!(r#"a = (-2,-2), b = (2,2), c = (-2,2)"#, two_midpoints(Point { x: -2, y: -2 }, Point { x: 2, y: 2 }, Point { x: -2, y: 2 }), (Point { x: 0, y: 0 }, Point { x: -2, y: 0 }));
}

#[test]
fn a_not_at_origin() {
    check!(r#"a = (4, 6), b = (0, 0), c = (8, 2)"#, two_midpoints(Point { x: 4, y: 6 }, Point { x: 0, y: 0 }, Point { x: 8, y: 2 }), (Point { x: 2, y: 3 }, Point { x: 6, y: 4 }));
}

#[test]
fn rounds_toward_zero() {
    check!(r#"a = (-3, -3), b = (0, 0), c = (0, 1)"#, two_midpoints(Point { x: -3, y: -3 }, Point { x: 0, y: 0 }, Point { x: 0, y: 1 }), (Point { x: -1, y: -1 }, Point { x: -1, y: -1 }));
}

#[test]
fn odd_sums() {
    check!(r#"a = (1, 1), b = (2, 2), c = (4, 5)"#, two_midpoints(Point { x: 1, y: 1 }, Point { x: 2, y: 2 }, Point { x: 4, y: 5 }), (Point { x: 1, y: 1 }, Point { x: 2, y: 3 }));
}

#[test]
fn order_of_results() {
    check!(r#"a = (0, 0), b = (10, 0), c = (0, 10)"#, two_midpoints(Point { x: 0, y: 0 }, Point { x: 10, y: 0 }, Point { x: 0, y: 10 }), (Point { x: 5, y: 0 }, Point { x: 0, y: 5 }));
}

#[test]
fn big_coordinates() {
    check!(r#"a = (5·10⁸, -5·10⁸), b = (5·10⁸, 5·10⁸), c = (-5·10⁸, -5·10⁸)"#, two_midpoints(Point { x: 500_000_000, y: -500_000_000 }, Point { x: 500_000_000, y: 500_000_000 }, Point { x: -500_000_000, y: -500_000_000 }), (Point { x: 500_000_000, y: 0 }, Point { x: 0, y: -500_000_000 }));
}

#[test]
fn all_three_usable_after() {
    check!(r#"a, b, c used again after two_midpoints"#, { let (a, b, c) = (Point { x: 1, y: 2 }, Point { x: 3, y: 4 }, Point { x: 5, y: 6 }); let _ = two_midpoints(a, b, c); (a, b, c) }, (Point { x: 1, y: 2 }, Point { x: 3, y: 4 }, Point { x: 5, y: 6 }));
}

fn is_copy<T: Copy>(_: &T) -> bool {
    true
}

#[test]
fn point_is_copy() {
    check!("Point: Copy", is_copy(&Point { x: 0, y: 0 }), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1102);
    for _ in 0..300 {
        let v: Vec<i32> = rng.vec(6, -1000, 1000);
        let (a, b, c) = (Point { x: v[0], y: v[1] }, Point { x: v[2], y: v[3] }, Point { x: v[4], y: v[5] });
        let want = (Point { x: (v[0] + v[2]) / 2, y: (v[1] + v[3]) / 2 }, Point { x: (v[0] + v[4]) / 2, y: (v[1] + v[5]) / 2 });
        check!(format!("a = {a:?}, b = {b:?}, c = {c:?}"), two_midpoints(a, b, c), want);
    }
}
