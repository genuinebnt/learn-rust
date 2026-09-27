pub fn minutes_to_rot(grid: &[Vec<u8>]) -> Option<u32> {
    let mut g = grid.to_vec();
    let (h, w) = (g.len(), g[0].len());
    let mut minutes = 0;
    loop {
        let mut next = g.clone();
        let mut fresh = 0;
        let mut changed = false;
        for r in 0..h {
            for c in 0..w {
                if g[r][c] != 1 {
                    continue;
                }
                let rotten_near = (r > 0 && g[r - 1][c] == 2) || (r + 1 < h && g[r + 1][c] == 2) || (c > 0 && g[r][c - 1] == 2) || (c + 1 < w && g[r][c + 1] == 2);
                if rotten_near {
                    next[r][c] = 2;
                    changed = true;
                } else {
                    fresh += 1;
                }
            }
        }
        if !changed {
            return (fresh == 0).then_some(minutes);
        }
        g = next;
        minutes += 1;
    }
}
