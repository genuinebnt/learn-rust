pub fn largest_island(grid: &[Vec<u8>]) -> usize {
    let (h, w) = (grid.len(), grid[0].len());
    let mut label = vec![vec![0usize; w]; h];
    let mut size = vec![0usize];
    for sr in 0..h {
        for sc in 0..w {
            if grid[sr][sc] != 1 || label[sr][sc] != 0 {
                continue;
            }
            let id = size.len();
            label[sr][sc] = id;
            let mut stack = vec![(sr, sc)];
            let mut count = 0;
            while let Some((r, c)) = stack.pop() {
                count += 1;
                for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
                    if nr < h && nc < w && grid[nr][nc] == 1 && label[nr][nc] == 0 {
                        label[nr][nc] = id;
                        stack.push((nr, nc));
                    }
                }
            }
            size.push(count);
        }
    }
    let mut best = 0;
    for r in 0..h {
        for c in 0..w {
            if grid[r][c] == 0 {
                let mut ids: Vec<usize> = Vec::new();
                for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
                    if nr < h && nc < w && label[nr][nc] != 0 && !ids.contains(&label[nr][nc]) {
                        ids.push(label[nr][nc]);
                    }
                }
                best = best.max(1 + ids.iter().map(|&id| size[id]).sum::<usize>());
            }
        }
    }
    best
}
