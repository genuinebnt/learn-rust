use std::collections::HashMap;

pub fn max_points(points: &[(i32, i32)]) -> usize {
    let mut best = points.len().min(2);
    for (i, &(x1, y1)) in points.iter().enumerate() {
        let mut slopes: HashMap<u64, usize> = HashMap::new();
        let mut same = 0;
        for &(x2, y2) in &points[i + 1..] {
            let (dx, dy) = (x2 as f64 - x1 as f64, y2 as f64 - y1 as f64);
            if dx == 0.0 && dy == 0.0 {
                same += 1;
                continue;
            }
            let slope = if dx == 0.0 { f64::INFINITY } else { dy / dx + 0.0 };
            *slopes.entry(slope.to_bits()).or_insert(0) += 1;
        }
        best = best.max(1 + same + slopes.values().copied().max().unwrap_or(0));
    }
    best
}
