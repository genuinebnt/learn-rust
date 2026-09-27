pub fn combination_sum2(candidates: &[u32], target: u32) -> Vec<Vec<u32>> {
    fn go(c: &[u32], start: usize, left: u32, path: &mut Vec<u32>, out: &mut std::collections::BTreeSet<Vec<u32>>) {
        if left == 0 {
            out.insert(path.clone());
            return;
        }
        for i in start..c.len() {
            if c[i] > left {
                break;
            }
            path.push(c[i]);
            go(c, i + 1, left - c[i], path, out);
            path.pop();
        }
    }
    let mut c = candidates.to_vec();
    c.sort_unstable();
    let mut out = std::collections::BTreeSet::new();
    go(&c, 0, target, &mut Vec::new(), &mut out);
    out.into_iter().collect()
}
