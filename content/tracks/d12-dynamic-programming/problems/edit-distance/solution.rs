pub fn edit_distance(a: &str, b: &str) -> usize {
    let a: Vec<char> = a.chars().collect();
    let b: Vec<char> = b.chars().collect();
    // prev[j] = edits between a[..i] and b[..j]; row 0 is j inserts.
    let mut prev: Vec<usize> = (0..=b.len()).collect();
    let mut cur = vec![0usize; b.len() + 1];
    for (i, &x) in a.iter().enumerate() {
        cur[0] = i + 1; // delete all of a[..=i]
        for (j, &y) in b.iter().enumerate() {
            cur[j + 1] = if x == y {
                prev[j]
            } else {
                1 + prev[j].min(prev[j + 1]).min(cur[j]) // replace, delete, insert
            };
        }
        std::mem::swap(&mut prev, &mut cur);
    }
    prev[b.len()]
}
