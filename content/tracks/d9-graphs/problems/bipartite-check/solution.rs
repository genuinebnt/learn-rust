use std::collections::VecDeque;

pub fn is_bipartite(adj: &[Vec<usize>]) -> bool {
    let mut side: Vec<Option<bool>> = vec![None; adj.len()];
    for start in 0..adj.len() {
        if side[start].is_some() {
            continue;
        }
        side[start] = Some(false);
        let mut queue = VecDeque::from([start]);
        while let Some(u) = queue.pop_front() {
            let s = side[u].expect("queued nodes are coloured");
            for &v in &adj[u] {
                match side[v] {
                    None => {
                        side[v] = Some(!s);
                        queue.push_back(v);
                    }
                    Some(t) if t == s => return false,
                    Some(_) => {}
                }
            }
        }
    }
    true
}
