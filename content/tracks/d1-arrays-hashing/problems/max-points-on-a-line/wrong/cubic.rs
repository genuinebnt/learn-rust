pub fn max_points(points: &[(i32, i32)]) -> usize {
    let n = points.len();
    let mut best = n.min(2);
    for i in 0..n {
        for j in i + 1..n {
            let (ax, ay) = (points[j].0 as i64 - points[i].0 as i64, points[j].1 as i64 - points[i].1 as i64);
            if ax == 0 && ay == 0 {
                best = best.max(points.iter().filter(|&&p| p == points[i]).count());
                continue;
            }
            let on = points.iter().filter(|&&(x, y)| ax * (y as i64 - points[i].1 as i64) == ay * (x as i64 - points[i].0 as i64)).count();
            best = best.max(on);
        }
    }
    best
}
