pub fn partition_labels(s: &str) -> Vec<usize> {
    let b = s.as_bytes();
    let mut sizes = Vec::new();
    let (mut start, mut end) = (0, 0);
    for i in 0..b.len() {
        let mut last = i;
        for j in (i..b.len()).rev() {
            if b[j] == b[i] {
                last = j;
                break;
            }
        }
        end = end.max(last);
        if i == end {
            sizes.push(end - start + 1);
            start = i + 1;
        }
    }
    sizes
}
