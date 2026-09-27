use std::iter::Sum;
use std::ops::{Add, AddAssign, Mul, Neg, Sub};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub struct Vec2 {
    pub x: i64,
    pub y: i64,
}

// TODO: the operator impls.

/// The sum of all the points.
pub fn total(points: &[Vec2]) -> Vec2 {
    points.iter().sum()
}

/// Start at the origin and take each step `count` times.
pub fn walk(steps: &[(Vec2, i64)]) -> Vec2 {
    let mut p = Vec2::default();
    for &(d, count) in steps {
        p += d * count;
    }
    p
}
