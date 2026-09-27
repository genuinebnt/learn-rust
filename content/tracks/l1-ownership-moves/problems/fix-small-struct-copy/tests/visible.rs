use solution::*;

#[test]
fn midpoints() {
    check!(r#"a = (0,0), b = (2,2), c = (4,0)"#, two_midpoints(Point { x: 0, y: 0 }, Point { x: 2, y: 2 }, Point { x: 4, y: 0 }), (Point { x: 1, y: 1 }, Point { x: 2, y: 0 }));
}

#[test]
fn reuse_after_call() {
    check!(r#"a = (1, 1) used after passing by value"#, { let a = Point { x: 1, y: 1 }; let _ = midpoint(a, a); a }, Point { x: 1, y: 1 });
}
