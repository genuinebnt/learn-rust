pub fn min_distance(a: &str, b: &str) -> usize {
    let (x, y) = (a.as_bytes(), b.as_bytes());
    let mut prev: Vec<usize> = (0..=y.len()).collect();
    let mut cur = vec![0usize; y.len() + 1];
    for (i, &p) in x.iter().enumerate() {
        cur[0] = i + 1;
        for (j, &q) in y.iter().enumerate() {
            cur[j + 1] = if p == q { prev[j] } else { 1 + prev[j].min(prev[j + 1]).min(cur[j]) };
        }
        std::mem::swap(&mut prev, &mut cur);
    }
    prev[y.len()]
}
