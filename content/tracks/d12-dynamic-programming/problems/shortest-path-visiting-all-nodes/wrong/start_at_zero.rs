use std::collections::VecDeque;

pub fn shortest_path_length(graph: &[Vec<usize>]) -> usize {
    let n = graph.len();
    if n <= 1 {
        return 0;
    }
    let all = (1usize << n) - 1;
    let mut seen = vec![vec![false; 1 << n]; n];
    let mut queue = VecDeque::new();
    seen[0][1] = true;
    queue.push_back((0, 1usize, 0));
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
    unreachable!()
}
