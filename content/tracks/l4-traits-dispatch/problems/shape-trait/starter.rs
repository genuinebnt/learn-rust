use std::f64::consts::PI;

pub struct Circle {
    pub r: f64,
}

pub struct Rect {
    pub w: f64,
    pub h: f64,
}

/// Another trait with a `name` method. Don't change it.
pub trait Label {
    fn name(&self) -> String;
}

impl Label for Rect {
    fn name(&self) -> String {
        "box".to_string()
    }
}

// TODO: the Named and Shape traits, and their impls for Circle and Rect.

/// Total number of sides across the shapes.
pub fn total_sides<S: Shape>(shapes: &[S]) -> u32 {
    S::SIDES * shapes.len() as u32
}

/// "<Named name>/<Label name>" for a rect: "rect/box".
pub fn both_names(r: &Rect) -> String {
    todo!()
}
