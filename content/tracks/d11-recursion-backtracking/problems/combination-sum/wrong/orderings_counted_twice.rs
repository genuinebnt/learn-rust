pub fn combination_sum(candidates: &[u32], target: u32) -> Vec<Vec<u32>> {
    fn go(c: &[u32], left: u32, path: &mut Vec<u32>, out: &mut Vec<Vec<u32>>) {
        if left == 0 {
            out.push(path.clone());
            return;
        }
        for &x in c {
            if x <= left {
                path.push(x);
                go(c, left - x, path, out);
                path.pop();
            }
        }
    }
    let mut out = Vec::new();
    go(candidates, target, &mut Vec::new(), &mut out);
    out
}
