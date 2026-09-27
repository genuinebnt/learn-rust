/// Appends a copy of every element: [1, 2] → [1, 2, 1, 2].
pub fn double_up(v: &mut Vec<i32>) {
    let n = v.len();
    for i in 0..n {
        let x = v[2 * i];
        v.insert(2 * i + 1, x);
    }
}
