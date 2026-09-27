pub fn partition_labels(s: &str) -> Vec<usize> {
    let bytes = s.as_bytes();
    let mut last = [0usize; 26];
    for (i, &b) in bytes.iter().enumerate() {
        last[(b - b'a') as usize] = i;
    }
    let mut sizes = Vec::new();
    let (mut start, mut end) = (0, 0);
    for (i, &b) in bytes.iter().enumerate() {
        end = end.max(last[(b - b'a') as usize]);
        if i == end {
            sizes.push(end - start + 1);
            start = i + 1;
        }
    }
    sizes
}
