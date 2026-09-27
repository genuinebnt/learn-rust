use std::collections::VecDeque;

pub fn shortest_path_length(graph: &[Vec<usize>]) -> usize {
    let n = graph.len();
    if n <= 1 {
        return 0;
    }
    let all = (1usize << n) - 1;
    // A state is (where we are, which nodes we've visited). BFS from every start at once.
    let mut seen = vec![vec![false; 1 << n]; n];
    let mut queue = VecDeque::new();
    for u in 0..n {
        seen[u][1 << u] = true;
        queue.push_back((u, 1usize << u, 0));
    }
    while let Some((u, visited, dist)) = queue.pop_front() {
        for &v in &graph[u] {
            let next = visited | 1 << v;
            if next == all {
                return dist + 1;
            }
            if !seen[v][next] {
                seen[v][next] = true;
                queue.push_back((v, next, dist + 1));
            }
        }
    }
    unreachable!("the graph is connected")
}
