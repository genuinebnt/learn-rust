use solution::*;

#[test]
fn midpoints() {
    check!(r#"a = (0,0), b = (2,2), c = (4,0)"#, two_midpoints(Point { x: 0, y: 0 }, Point { x: 2, y: 2 }, Point { x: 4, y: 0 }), (Point { x: 1, y: 1 }, Point { x: 2, y: 0 }));
}

#[test]
fn reuse_after_call() {
    check!(r#"a = (1, 1) used after passing by value"#, { let a = Point { x: 1, y: 1 }; let _ = midpoint(a, a); a }, Point { x: 1, y: 1 });
}

#[test]
fn all_same() {
    check!(r#"a = b = c = (3, 5)"#, two_midpoints(Point { x: 3, y: 5 }, Point { x: 3, y: 5 }, Point { x: 3, y: 5 }), (Point { x: 3, y: 5 }, Point { x: 3, y: 5 }));
}

#[test]
fn odd_sums_truncate() {
    check!(r#"a = (0, 0), b = (1, 3), c = (-1, -3)"#, two_midpoints(Point { x: 0, y: 0 }, Point { x: 1, y: 3 }, Point { x: -1, y: -3 }), (Point { x: 0, y: 1 }, Point { x: 0, y: -1 }));
}

#[test]
fn b_usable_after() {
    check!(r#"b used again after two_midpoints"#, { let b = Point { x: 2, y: 2 }; let _ = two_midpoints(Point { x: 0, y: 0 }, b, Point { x: 4, y: 4 }); b }, Point { x: 2, y: 2 });
}
