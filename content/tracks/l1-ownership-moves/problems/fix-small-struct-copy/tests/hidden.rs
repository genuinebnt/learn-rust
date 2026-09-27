use solution::*;

#[test]
fn negative() {
    check!(r#"a = (-2,-2), b = (2,2), c = (-2,2)"#, two_midpoints(Point { x: -2, y: -2 }, Point { x: 2, y: 2 }, Point { x: -2, y: 2 }), (Point { x: 0, y: 0 }, Point { x: -2, y: 0 }));
}
