use std::collections::VecDeque;

struct Matcher {
    adj: Vec<Vec<usize>>,
    match_l: Vec<Option<usize>>,
    match_r: Vec<Option<usize>>,
    dist: Vec<u32>,
    cursor: Vec<usize>,
}

impl Matcher {
    /// Layers the left side by BFS from free left nodes. True if some free right node is reachable.
    fn layer(&mut self) -> bool {
        let mut queue = VecDeque::new();
        for u in 0..self.adj.len() {
            if self.match_l[u].is_none() {
                self.dist[u] = 0;
                queue.push_back(u);
            } else {
                self.dist[u] = u32::MAX;
            }
        }
        let mut found = false;
        while let Some(u) = queue.pop_front() {
            for &v in &self.adj[u] {
                match self.match_r[v] {
                    None => found = true,
                    Some(w) if self.dist[w] == u32::MAX => {
                        self.dist[w] = self.dist[u] + 1;
                        queue.push_back(w);
                    }
                    Some(_) => {}
                }
            }
        }
        found
    }

    fn augment(&mut self, u: usize) -> bool {
        while self.cursor[u] < self.adj[u].len() {
            let v = self.adj[u][self.cursor[u]];
            self.cursor[u] += 1;
            let ok = match self.match_r[v] {
                None => true,
                Some(w) => self.dist[w] == self.dist[u] + 1 && self.augment(w),
            };
            if ok {
                self.match_l[u] = Some(v);
                self.match_r[v] = Some(u);
                return true;
            }
        }
        self.dist[u] = u32::MAX;
        false
    }
}

pub fn max_matching(left: usize, right: usize, edges: &[(usize, usize)]) -> usize {
    let mut adj = vec![Vec::new(); left];
    for &(u, v) in edges {
        adj[u].push(v);
    }
    let mut m = Matcher { adj, match_l: vec![None; left], match_r: vec![None; right], dist: vec![0; left], cursor: vec![0; left] };
    let mut size = 0;
    while m.layer() {
        m.cursor.fill(0);
        for u in 0..left {
            if m.match_l[u].is_none() && m.augment(u) {
                size += 1;
            }
        }
    }
    size
}
