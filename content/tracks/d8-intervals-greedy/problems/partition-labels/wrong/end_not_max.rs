pub fn partition_labels(s: &str) -> Vec<usize> {
    let bytes = s.as_bytes();
    let mut last = [0usize; 26];
    for (i, &b) in bytes.iter().enumerate() {
        last[(b - b'a') as usize] = i;
    }
    let mut sizes = Vec::new();
    let mut start = 0;
    for (i, &b) in bytes.iter().enumerate() {
        if last[(b - b'a') as usize] == i {
            sizes.push(i - start + 1);
            start = i + 1;
        }
    }
    sizes
}
