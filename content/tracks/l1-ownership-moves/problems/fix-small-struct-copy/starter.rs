#[derive(Debug, PartialEq)]
pub struct Point {
    pub x: i32,
    pub y: i32,
}

pub fn midpoint(a: Point, b: Point) -> Point {
    Point { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 }
}

/// The midpoints of a→b and a→c.
pub fn two_midpoints(a: Point, b: Point, c: Point) -> (Point, Point) {
    (midpoint(a, b), midpoint(a, c))
}
