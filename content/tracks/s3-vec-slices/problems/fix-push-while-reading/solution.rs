/// Appends a copy of every element: [1, 2] → [1, 2, 1, 2].
pub fn double_up(v: &mut Vec<i32>) {
    v.extend_from_within(..);
}
