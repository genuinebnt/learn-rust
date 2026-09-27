use solution::*;

#[test]
fn wall_at_the_end_of_a_row() {
    check!(r#"grid = ["....#"]"#, min_walls(&["....#"]), 1);
}

#[test]
fn diagonal_walls() {
    check!(r###"grid = [".##", "#.#", "##."]"###, min_walls(&[".##", "#.#", "##."]), 2);
}

#[test]
fn one_wall_beats_a_dead_end() {
    check!(r#####"grid = [".#...", ".#.#.", "...##", "####."]"#####, min_walls(&[".#...", ".#.#.", "...##", "####."]), 1);
}

#[test]
fn alternating_row() {
    check!(r#"grid = [".#.#.#."]"#, min_walls(&[".#.#.#."]), 3);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(919);
    for _ in 0..300 {
        let h = 1 + rng.below(5);
        let w = 1 + rng.below(5);
        let mut rows: Vec<String> = (0..h).map(|_| rng.string(w, "..#")).collect();
        rows[0].replace_range(0..1, ".");
        let grid: Vec<&str> = rows.iter().map(|s| s.as_str()).collect();
        // Brute force: relax every cell until nothing changes.
        let cost = |r: usize, c: usize| u32::from(rows[r].as_bytes()[c] == b'#');
        let mut dist = vec![vec![u32::MAX; w]; h];
        dist[0][0] = 0;
        let mut changed = true;
        while changed {
            changed = false;
            for r in 0..h {
                for c in 0..w {
                    for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
                        if nr < h && nc < w && dist[nr][nc] != u32::MAX && dist[nr][nc] + cost(r, c) < dist[r][c] {
                            dist[r][c] = dist[nr][nc] + cost(r, c);
                            changed = true;
                        }
                    }
                }
            }
        }
        check!(format!("grid = {rows:?}"), min_walls(&grid), dist[h - 1][w - 1]);
    }
}

#[test]
fn walled_target() {
    check!(r#"grid = [".#"]"#, min_walls(&[".#"]), 1);
}

#[test]
fn detour_is_free() {
    check!(r###"grid = ["..#", "##.", "..."]"###, min_walls(&["..#", "##.", "..."]), 1);
}

#[test]
fn solid_rock() {
    let first = format!(".{}", "#".repeat(499));
    let rest = "#".repeat(500);
    let grid: Vec<&str> = (0..500).map(|i| if i == 0 { first.as_str() } else { rest.as_str() }).collect();
    check!(r#"500×500, all walls except the start"#, min_walls(&grid), 998);
}

#[test]
fn maze() {
    let rows: Vec<String> = (0..499).map(|r| if r % 2 == 0 { ".".repeat(500) } else if r % 4 == 1 { format!("{}.", "#".repeat(499)) } else { format!(".{}", "#".repeat(499)) }).collect();
    let grid: Vec<&str> = rows.iter().map(|s| s.as_str()).collect();
    check!(r#"499×500 snake of free corridors"#, min_walls(&grid), 0);
}
