use std::collections::VecDeque;

pub fn is_bipartite(adj: &[Vec<usize>]) -> bool {
    if adj.is_empty() {
        return true;
    }
    let mut side: Vec<Option<bool>> = vec![None; adj.len()];
    side[0] = Some(false);
    let mut queue = VecDeque::from([0]);
    while let Some(u) = queue.pop_front() {
        let s = side[u].unwrap();
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
    true
}
