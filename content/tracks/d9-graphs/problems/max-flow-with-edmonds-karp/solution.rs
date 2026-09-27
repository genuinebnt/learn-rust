use std::collections::VecDeque;

pub struct FlowNetwork {
    /// Edge ids leaving each node.
    adj: Vec<Vec<usize>>,
    to: Vec<usize>,
    /// Residual capacity. Edge `e ^ 1` is the reverse of edge `e`.
    cap: Vec<u64>,
}

impl FlowNetwork {
    pub fn new(n: usize) -> Self {
        FlowNetwork { adj: vec![Vec::new(); n], to: Vec::new(), cap: Vec::new() }
    }

    pub fn add_edge(&mut self, u: usize, v: usize, cap: u64) {
        self.adj[u].push(self.to.len());
        self.to.push(v);
        self.cap.push(cap);
        self.adj[v].push(self.to.len());
        self.to.push(u);
        self.cap.push(0);
    }

    pub fn max_flow(&mut self, s: usize, t: usize) -> u64 {
        let n = self.adj.len();
        let mut total = 0;
        loop {
            let mut via: Vec<Option<usize>> = vec![None; n];
            let mut seen = vec![false; n];
            seen[s] = true;
            let mut queue = VecDeque::from([s]);
            while let Some(u) = queue.pop_front() {
                for &e in &self.adj[u] {
                    let v = self.to[e];
                    if !seen[v] && self.cap[e] > 0 {
                        seen[v] = true;
                        via[v] = Some(e);
                        queue.push_back(v);
                    }
                }
            }
            if !seen[t] {
                return total;
            }
            let mut push = u64::MAX;
            let mut v = t;
            while let Some(e) = via[v] {
                push = push.min(self.cap[e]);
                v = self.to[e ^ 1];
            }
            let mut v = t;
            while let Some(e) = via[v] {
                self.cap[e] -= push;
                self.cap[e ^ 1] += push;
                v = self.to[e ^ 1];
            }
            total += push;
        }
    }
}
