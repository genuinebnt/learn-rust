use std::collections::VecDeque;

pub fn shortest_path_binary_matrix(grid: &[Vec<u8>]) -> Option<usize> {
    let n = grid.len();
    if grid[0][0] == 1 || grid[n - 1][n - 1] == 1 {
        return None;
    }
    let mut dist = vec![vec![0usize; n]; n];
    dist[0][0] = 1;
    let mut queue = VecDeque::from([(0usize, 0usize)]);
    while let Some((r, c)) = queue.pop_front() {
        if (r, c) == (n - 1, n - 1) {
            return Some(dist[r][c]);
        }
        for dr in [usize::MAX, 0, 1] {
            for dc in [usize::MAX, 0, 1] {
                let (nr, nc) = (r.wrapping_add(dr), c.wrapping_add(dc));
                if nr < n && nc < n && grid[nr][nc] == 0 && dist[nr][nc] == 0 {
                    dist[nr][nc] = dist[r][c] + 1;
                    queue.push_back((nr, nc));
                }
            }
        }
    }
    None
}
