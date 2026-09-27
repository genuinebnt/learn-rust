fn best(dist: &[Vec<usize>], last: usize, used: &mut Vec<bool>, left: usize) -> usize {
    if left == 0 {
        return 0;
    }
    let mut top = usize::MAX;
    for v in 0..dist.len() {
        if !used[v] {
            used[v] = true;
            top = top.min(dist[last][v] + best(dist, v, used, left - 1));
            used[v] = false;
        }
    }
    top
}

pub fn shortest_path_length(graph: &[Vec<usize>]) -> usize {
    let n = graph.len();
    let mut dist = vec![vec![usize::MAX / 4; n]; n];
    for u in 0..n {
        dist[u][u] = 0;
        for &v in &graph[u] {
            dist[u][v] = 1;
        }
    }
    for k in 0..n {
        for i in 0..n {
            for j in 0..n {
                dist[i][j] = dist[i][j].min(dist[i][k] + dist[k][j]);
            }
        }
    }
    let mut top = 0;
    for s in 0..n {
        let mut used = vec![false; n];
        used[s] = true;
        let b = best(&dist, s, &mut used, n - 1);
        top = if s == 0 { b } else { top.min(b) };
    }
    top
}
