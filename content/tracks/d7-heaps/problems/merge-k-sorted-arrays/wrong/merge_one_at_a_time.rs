pub fn merge_k_sorted(arrays: &[Vec<i32>]) -> Vec<i32> {
    let mut acc: Vec<i32> = Vec::new();
    for v in arrays {
        let mut merged = Vec::with_capacity(acc.len() + v.len());
        let (mut i, mut j) = (0, 0);
        while i < acc.len() || j < v.len() {
            if j == v.len() || (i < acc.len() && acc[i] <= v[j]) {
                merged.push(acc[i]);
                i += 1;
            } else {
                merged.push(v[j]);
                j += 1;
            }
        }
        acc = merged;
    }
    acc
}
