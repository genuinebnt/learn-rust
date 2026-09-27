pub fn combination_sum3(k: usize, n: u32) -> Vec<Vec<u32>> {
    fn go(next: u32, k: usize, left: u32, path: &mut Vec<u32>, out: &mut Vec<Vec<u32>>) {
        if path.len() == k {
            if left == 0 {
                out.push(path.clone());
            }
            return;
        }
        for d in next..=9 {
            if d > left {
                break;
            }
            path.push(d);
            go(d + 1, k, left - d, path, out);
            path.pop();
        }
    }
    let mut out = Vec::new();
    go(1, k, n, &mut Vec::with_capacity(k), &mut out);
    out
}
