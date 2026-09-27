pub fn asteroid_collision(asteroids: &[i32]) -> Vec<i32> {
    let mut v = asteroids.to_vec();
    while let Some(i) = (0..v.len().saturating_sub(1)).find(|&i| v[i] > 0 && v[i + 1] < 0) {
        let (l, r) = (v[i], -v[i + 1]);
        if l > r {
            v.remove(i + 1);
        } else if l < r {
            v.remove(i);
        } else {
            v.drain(i..i + 2);
        }
    }
    v
}
