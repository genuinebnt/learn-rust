pub fn combine(n: u32, k: u32) -> Vec<Vec<u32>> {
    fn go(next: u32, n: u32, k: usize, path: &mut Vec<u32>, out: &mut Vec<Vec<u32>>) {
        if path.len() == k {
            out.push(path.clone());
            return;
        }
        for x in next..=n {
            path.push(x);
            go(x + 1, n, k, path, out);
            path.pop();
        }
    }
    let mut out = Vec::new();
    go(1, n, k as usize, &mut Vec::new(), &mut out);
    out
}
