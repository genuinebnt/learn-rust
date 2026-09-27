use solution::*;

fn run(rows: &[&str]) -> Vec<String> {
    let mut board: Vec<Vec<char>> = rows.iter().map(|r| r.chars().collect()).collect();
    capture_regions(&mut board);
    board.iter().map(|r| r.iter().collect()).collect()
}

#[test]
fn all_o() {
    check!(r#"board = ["OOO", "OOO", "OOO"]"#, run(&["OOO", "OOO", "OOO"]), vec!["OOO", "OOO", "OOO"]);
}

#[test]
fn one_row() {
    check!(r#"board = ["OXO"]"#, run(&["OXO"]), vec!["OXO"]);
}

#[test]
fn two_inner_regions() {
    check!(r#"board = ["XXXXX", "XOXOX", "XXXXX"]"#, run(&["XXXXX", "XOXOX", "XXXXX"]), vec!["XXXXX", "XXXXX", "XXXXX"]);
}

#[test]
fn ring_of_o_around_x() {
    check!(r#"board = ["XXXXX", "XOOOX", "XOXOX", "XOOOX", "XXXXX"]"#, run(&["XXXXX", "XOOOX", "XOXOX", "XOOOX", "XXXXX"]), vec!["XXXXX", "XXXXX", "XXXXX", "XXXXX", "XXXXX"]);
}

#[test]
fn region_touching_the_bottom() {
    check!(r#"board = ["XXX", "XOX", "XOX"]"#, run(&["XXX", "XOX", "XOX"]), vec!["XXX", "XOX", "XOX"]);
}

#[test]
fn inner_region_captured_big() {
    let mut b: Vec<Vec<char>> = (0..500).map(|r| (0..500).map(|c| if r == 0 || c == 0 || r == 499 || c == 499 { 'X' } else { 'O' }).collect()).collect();
    capture_regions(&mut b);
    check!(r#"500×500: X border, O inside"#, (b[1][1], b[250][250], b[0][0], b.iter().flatten().filter(|&&ch| ch == 'O').count()), ('X', 'X', 'X', 0));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(943);
    for _ in 0..300 {
        let (h, w) = (1 + rng.below(6), 1 + rng.below(6));
        let rows: Vec<String> = (0..h).map(|_| rng.string(w, "XOO")).collect();
        let cells: Vec<Vec<char>> = rows.iter().map(|r| r.chars().collect()).collect();
        // Brute force: grow the safe set from the border until it stops changing.
        let mut safe: Vec<Vec<bool>> = (0..h).map(|r| (0..w).map(|c| cells[r][c] == 'O' && (r == 0 || c == 0 || r == h - 1 || c == w - 1)).collect()).collect();
        let mut changed = true;
        while changed {
            changed = false;
            for r in 0..h {
                for c in 0..w {
                    let near = [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)];
                    if cells[r][c] == 'O' && !safe[r][c] && near.iter().any(|&(a, b)| a < h && b < w && safe[a][b]) {
                        safe[r][c] = true;
                        changed = true;
                    }
                }
            }
        }
        let want: Vec<String> = (0..h).map(|r| (0..w).map(|c| if safe[r][c] { 'O' } else { 'X' }).collect()).collect();
        let refs: Vec<&str> = rows.iter().map(|s| s.as_str()).collect();
        check!(format!("board = {rows:?}"), run(&refs), want);
    }
}

#[test]
fn scale_snake_reaches_the_border() {
    // A 125249-cell corridor of 'O' winding through the board from the top row.
    let mut b: Vec<Vec<char>> = (0..499).map(|r| (0..500).map(|c| if r % 2 == 0 || (r % 4 == 1 && c == 499) || (r % 4 == 3 && c == 0) { 'O' } else { 'X' }).collect()).collect();
    capture_regions(&mut b);
    let kept = b.iter().flatten().filter(|&&ch| ch == 'O').count();
    check!("499×500 snake of 'O' joined to the border", kept, 125_249);
}
