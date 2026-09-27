pub fn find_order(n: usize, prereqs: &[(usize, usize)]) -> Option<Vec<usize>> {
    // Postorder DFS without the final reverse: every course lands after the courses it unlocks.
    let mut adj = vec![Vec::new(); n];
    for &(a, b) in prereqs {
        adj[a].push(b);
    }
    let mut state = vec![0u8; n];
    let mut out = Vec::new();
    for s in 0..n {
        if state[s] != 0 {
            continue;
        }
        let mut stack = vec![(s, 0)];
        state[s] = 1;
        while let Some(&mut (u, ref mut i)) = stack.last_mut() {
            if *i < adj[u].len() {
                let v = adj[u][*i];
                *i += 1;
                match state[v] {
                    0 => {
                        state[v] = 1;
                        stack.push((v, 0));
                    }
                    1 => return None,
                    _ => {}
                }
            } else {
                state[u] = 2;
                out.push(u);
                stack.pop();
            }
        }
    }
    Some(out)
}
