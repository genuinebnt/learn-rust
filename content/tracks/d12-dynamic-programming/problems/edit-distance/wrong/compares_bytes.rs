pub fn edit_distance(a: &str, b: &str) -> usize {
    let (a, b) = (a.as_bytes(), b.as_bytes());
    let mut prev: Vec<usize> = (0..=b.len()).collect();
    let mut cur = vec![0usize; b.len() + 1];
    for (i, &x) in a.iter().enumerate() {
        cur[0] = i + 1;
        for (j, &y) in b.iter().enumerate() {
            cur[j + 1] = if x == y { prev[j] } else { 1 + prev[j].min(prev[j + 1]).min(cur[j]) };
        }
        std::mem::swap(&mut prev, &mut cur);
    }
    prev[b.len()]
}
