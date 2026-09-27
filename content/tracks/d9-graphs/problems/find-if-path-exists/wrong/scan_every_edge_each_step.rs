pub fn valid_path(n: usize, edges: &[(usize, usize)], source: usize, destination: usize) -> bool {
    let mut seen = vec![false; n];
    seen[source] = true;
    let mut stack = vec![source];
    while let Some(u) = stack.pop() {
        if u == destination {
            return true;
        }
        for &(a, b) in edges {
            let v = if a == u { b } else if b == u { a } else { continue };
            if !seen[v] {
                seen[v] = true;
                stack.push(v);
            }
        }
    }
    false
}
