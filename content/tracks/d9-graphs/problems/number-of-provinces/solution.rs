pub fn count_provinces(connected: &[Vec<u8>]) -> usize {
    let n = connected.len();
    let mut seen = vec![false; n];
    let mut provinces = 0;
    for start in 0..n {
        if seen[start] {
            continue;
        }
        provinces += 1;
        seen[start] = true;
        let mut stack = vec![start];
        while let Some(u) = stack.pop() {
            for v in 0..n {
                if connected[u][v] == 1 && !seen[v] {
                    seen[v] = true;
                    stack.push(v);
                }
            }
        }
    }
    provinces
}
