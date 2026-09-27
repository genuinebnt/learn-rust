use solution::*;

#[test]
fn keys_in_passing() {
    check!(r#"grid = ["@ab"]"#, shortest_path_all_keys(&["@ab"]), Some(2));
}

#[test]
fn walled_off() {
    check!(r#"grid = ["@#a"]"#, shortest_path_all_keys(&["@#a"]), None);
}

#[test]
fn cheaper_order() {
    check!(r#"grid = ["b..@.a"]"#, shortest_path_all_keys(&["b..@.a"]), Some(7));
}

#[test]
fn second_key_unreachable() {
    check!(r####"grid = ["@.a", "###", "A.b"]"####, shortest_path_all_keys(&["@.a", "###", "A.b"]), None);
}

#[test]
fn locks_in_a_cycle() {
    check!(r##"grid = ["a#@", "B.A", "#.b"]"##, shortest_path_all_keys(&["a#@", "B.A", "#.b"]), None);
}

#[test]
fn one_column() {
    check!(r#"grid = ["a", ".", "@", "b"]"#, shortest_path_all_keys(&["a", ".", "@", "b"]), Some(4));
}

#[test]
fn six_keys_in_a_row() {
    check!(r#"grid = ["@abcdef"]"#, shortest_path_all_keys(&["@abcdef"]), Some(6));
}

#[test]
fn random_vs_brute_force() {
    use std::collections::VecDeque;
    // Brute force: try every order of the keys, walking between them with the keys collected so far.
    fn walk(g: &[Vec<u8>], from: (usize, usize), to: (usize, usize), keys: u32) -> Option<u32> {
        let (h, w) = (g.len(), g[0].len());
        let mut dist = vec![vec![None; w]; h];
        dist[from.0][from.1] = Some(0);
        let mut queue = VecDeque::from([from]);
        while let Some((r, c)) = queue.pop_front() {
            let d = dist[r][c].unwrap();
            if (r, c) == to {
                return Some(d);
            }
            for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
                if nr >= h || nc >= w || dist[nr][nc].is_some() {
                    continue;
                }
                let cell = g[nr][nc];
                if cell == b'#' || (cell.is_ascii_uppercase() && keys & (1 << (cell - b'A')) == 0) {
                    continue;
                }
                dist[nr][nc] = Some(d + 1);
                queue.push_back((nr, nc));
            }
        }
        None
    }
    fn orders(k: usize) -> Vec<Vec<usize>> {
        if k == 0 {
            return vec![vec![]];
        }
        let mut out = Vec::new();
        for rest in orders(k - 1) {
            for i in 0..=rest.len() {
                let mut o = rest.clone();
                o.insert(i, k - 1);
                out.push(o);
            }
        }
        out
    }

    let mut rng = anneal_prelude::Rng::new(956);
    for _ in 0..300 {
        let (h, w) = (1 + rng.below(4), 2 + rng.below(4));
        let mut g: Vec<Vec<u8>> = (0..h).map(|_| (0..w).map(|_| if rng.below(4) == 0 { b'#' } else { b'.' }).collect()).collect();
        let mut cells: Vec<(usize, usize)> = (0..h).flat_map(|r| (0..w).map(move |c| (r, c))).collect();
        rng.shuffle(&mut cells);
        let k = rng.below(4).min((cells.len() - 1) / 2);
        g[cells[0].0][cells[0].1] = b'@';
        let mut spot = vec![(0, 0); k];
        for i in 0..k {
            spot[i] = cells[1 + i];
            g[spot[i].0][spot[i].1] = b'a' + i as u8;
            if rng.bool() {
                g[cells[1 + k + i].0][cells[1 + k + i].1] = b'A' + i as u8;
            }
        }
        let mut want: Option<u32> = None;
        for order in orders(k) {
            let (mut at, mut keys, mut total) = (cells[0], 0u32, Some(0));
            for &i in &order {
                total = match (total, walk(&g, at, spot[i], keys)) {
                    (Some(t), Some(d)) => Some(t + d),
                    _ => None,
                };
                at = spot[i];
                keys |= 1 << i;
            }
            if let Some(t) = total {
                want = Some(want.map_or(t, |x: u32| x.min(t)));
            }
        }
        let rows: Vec<String> = g.iter().map(|r| String::from_utf8(r.clone()).unwrap()).collect();
        let refs: Vec<&str> = rows.iter().map(|r| r.as_str()).collect();
        check!(format!("grid = {rows:?}"), shortest_path_all_keys(&refs), want);
    }
}

#[test]
fn largest_grid_six_keys() {
    let grid = [
        "......#.#..#....#...#..##.#...",
        "..##....##..#..#.....De.###...",
        "........#####..#...#.###..##.#",
        "...###...##.##..#...##...#.#.#",
        "##........#.......#.#.A.#...#.",
        ".#.#.#..#...........#.....##..",
        "...b#..#.##.#####.....#..#.#..",
        "###.......#.....###....#.#.#..",
        "...#........#.d..#...#....#..#",
        "....##.....#..###............#",
        ".#.##.#####.##..###.#.....##..",
        ".#.....#C..........##.......##",
        "#...#.....#.#...B..##...#..##.",
        "#....E##.##.###.##...#.#......",
        ".....##.....###...#.##......#.",
        ".###.###...#......#...#..##...",
        "..#.#..#.#...#...##.......#...",
        "..#........#..#.#.......#....#",
        "#.#..#....#..#..#........#....",
        ".#.##..........#.#...#..#..#..",
        "........#...##.#...#.#.......#",
        "#..####..a##.##.##F..#..#.###.",
        ".#..##.###.##..#.#...#.....#..",
        ".#.c....#.#...###.#.........#.",
        "#..##...#........#.#..#..#..#.",
        "#..#..#.#.###.....##....#.....",
        "f.....#..............#...#.#..",
        ".#...##..#.##..#.#...#.#@...#.",
        "........#....#..#.........#...",
        "......#.#...#..##.#..####.....",
    ];
    check!("30×30 grid, 30% walls, six keys and six locks", shortest_path_all_keys(&grid), Some(150));
}
