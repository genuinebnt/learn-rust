use solution::*;

#[test]
fn flat_route() {
    check!(r#"a 5×5 grid with a flat winding path"#, minimum_effort(&[vec![1, 2, 1, 1, 1], vec![1, 2, 1, 2, 1], vec![1, 2, 1, 2, 1], vec![1, 2, 1, 2, 1], vec![1, 1, 1, 2, 1]]), 0);
}

#[test]
fn single_cell() {
    check!(r#"heights = [[7]]"#, minimum_effort(&[vec![7]]), 0);
}

#[test]
fn big_drop() {
    check!(r#"heights = [[0, 1000000]]"#, minimum_effort(&[vec![0, 1_000_000]]), 1_000_000);
}

#[test]
fn column() {
    check!(r#"heights = [[4],[1],[9]]"#, minimum_effort(&[vec![4], vec![1], vec![9]]), 8);
}

#[test]
fn one_row_max_step() {
    check!(r#"heights = [[1,10,6,7,9,10,4,9]]"#, minimum_effort(&[vec![1, 10, 6, 7, 9, 10, 4, 9]]), 9);
}

#[test]
fn all_zero() {
    check!(r#"heights = [[0,0],[0,0]]"#, minimum_effort(&[vec![0, 0], vec![0, 0]]), 0);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(918);
    for _ in 0..300 {
        let h = 1 + rng.below(4);
        let w = 1 + rng.below(4);
        let heights: Vec<Vec<u32>> = (0..h).map(|_| rng.vec(w, 0, 20)).collect();
        // Brute force: the smallest limit under which a flood fill from the start reaches the end.
        let mut want = 0;
        loop {
            let mut seen = vec![vec![false; w]; h];
            seen[0][0] = true;
            let mut stack = vec![(0usize, 0usize)];
            while let Some((r, c)) = stack.pop() {
                for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
                    if nr < h && nc < w && !seen[nr][nc] && heights[r][c].abs_diff(heights[nr][nc]) <= want {
                        seen[nr][nc] = true;
                        stack.push((nr, nc));
                    }
                }
            }
            if seen[h - 1][w - 1] {
                break;
            }
            want += 1;
        }
        check!(format!("heights = {heights:?}"), minimum_effort(&heights), want);
    }
}

#[test]
fn scale_300x300() {
    let mut x: u64 = 12_345;
    let heights: Vec<Vec<u32>> = (0..300)
        .map(|_| (0..300).map(|_| { x = x.wrapping_mul(6_364_136_223_846_793_005).wrapping_add(1_442_695_040_888_963_407); ((x >> 33) % 1_000_001) as u32 }).collect())
        .collect();
    check!("300×300 pseudo-random heights up to 10⁶ (LCG seed 12345)", minimum_effort(&heights), 346_912);
}

#[test]
fn scale_many_distinct_steps() {
    // Flat 0 everywhere, a wall of 10⁶ in the last column, and 22350 isolated spikes of distinct heights 1, 2, ….
    let mut next = 0;
    let heights: Vec<Vec<u32>> = (0..300)
        .map(|r| (0..300).map(|c| if c == 299 { 1_000_000 } else if r % 2 == 0 && c % 2 == 0 && c <= 296 { next += 1; next } else { 0 }).collect())
        .collect();
    check!("300×300: flat, spikes 1..=22350, last column 10⁶", minimum_effort(&heights), 1_000_000);
}
