use std::collections::VecDeque;

pub fn min_cost_flow(n: usize, edges: &[(usize, usize, u32, i64)], s: usize, t: usize, want: u32) -> Option<i64> {
    let mut adj = vec![Vec::new(); n];
    let (mut to, mut cap, mut cost) = (Vec::new(), Vec::new(), Vec::new());
    for &(u, v, c, w) in edges {
        adj[u].push(to.len());
        to.push(v);
        cap.push(c);
        cost.push(w);
        adj[v].push(to.len());
        to.push(u);
        cap.push(0);
        cost.push(-w);
    }
    let (mut sent, mut total) = (0u32, 0i64);
    while sent < want {
        let mut dist = vec![i64::MAX; n];
        let mut via: Vec<Option<usize>> = vec![None; n];
        let mut queued = vec![false; n];
        dist[s] = 0;
        let mut queue = VecDeque::from([s]);
        while let Some(u) = queue.pop_front() {
            queued[u] = false;
            for &e in &adj[u] {
                let v = to[e];
                if cap[e] > 0 && dist[u] + cost[e] < dist[v] {
                    dist[v] = dist[u] + cost[e];
                    via[v] = Some(e);
                    if !queued[v] {
                        queued[v] = true;
                        queue.push_back(v);
                    }
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
            v = to[e ^ 1];
        }
        let mut v = t;
        while let Some(e) = via[v] {
            cap[e] -= push;
            cap[e ^ 1] += push;
            v = to[e ^ 1];
        }
        sent += push;
        total += dist[t];
    }
    Some(total)
}
