use std::collections::VecDeque;

pub fn min_cost_flow(n: usize, edges: &[(usize, usize, u32, i64)], s: usize, t: usize, want: u32) -> Option<i64> {
    let mut adj = vec![Vec::new(); n];
    let mut cap: Vec<u32> = Vec::new();
    for (e, &(u, _, c, _)) in edges.iter().enumerate() {
        adj[u].push(e);
        cap.push(c);
    }
    let (mut sent, mut total) = (0u32, 0i64);
    while sent < want {
        let mut dist = vec![i64::MAX; n];
        let mut via: Vec<Option<usize>> = vec![None; n];
        dist[s] = 0;
        let mut queue = VecDeque::from([s]);
        while let Some(u) = queue.pop_front() {
            for &e in &adj[u] {
                let (_, v, _, w) = edges[e];
                if cap[e] > 0 && dist[u] + w < dist[v] {
                    dist[v] = dist[u] + w;
                    via[v] = Some(e);
                    queue.push_back(v);
                }
            }
        }
        if dist[t] == i64::MAX {
            return None;
        }
        let mut push = want - sent;
        let mut v = t;
        while let Some(e) = via[v] {
            push = push.min(cap[e]);
            v = edges[e].0;
        }
        let mut v = t;
        while let Some(e) = via[v] {
            cap[e] -= push;
            v = edges[e].0;
        }
        sent += push;
        total += dist[t] * i64::from(push);
    }
    Some(total)
}
