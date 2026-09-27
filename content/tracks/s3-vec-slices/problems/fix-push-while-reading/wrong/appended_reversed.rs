/// Appends a copy of every element: [1, 2] → [1, 2, 1, 2].
pub fn double_up(v: &mut Vec<i32>) {
    for i in (0..v.len()).rev() {
        let x = v[i];
        v.push(x);
    }
}
