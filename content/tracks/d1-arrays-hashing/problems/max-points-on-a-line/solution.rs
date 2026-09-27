use std::collections::HashMap;

fn gcd(a: i64, b: i64) -> i64 {
    if b == 0 { a.abs() } else { gcd(b, a % b) }
}

pub fn max_points(points: &[(i32, i32)]) -> usize {
    let mut best = points.len().min(2);
    for (i, &(x1, y1)) in points.iter().enumerate() {
        let mut slopes: HashMap<(i64, i64), usize> = HashMap::new();
        let mut same = 0;
        for &(x2, y2) in &points[i + 1..] {
            let (mut dx, mut dy) = (x2 as i64 - x1 as i64, y2 as i64 - y1 as i64);
            if dx == 0 && dy == 0 {
                same += 1;
                continue;
            }
            let g = gcd(dx, dy);
            dx /= g;
            dy /= g;
            // One sign convention per direction.
            if dx < 0 || (dx == 0 && dy < 0) {
                dx = -dx;
                dy = -dy;
            }
            *slopes.entry((dx, dy)).or_insert(0) += 1;
        }
        let on_line = slopes.values().copied().max().unwrap_or(0);
        best = best.max(1 + same + on_line);
    }
    best
}
