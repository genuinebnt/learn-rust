fn on_board(g: &mut [Vec<u8>], r: usize, c: usize, w: &[u8]) -> bool {
    if g[r][c] != w[0] {
        return false;
    }
    if w.len() == 1 {
        return true;
    }
    let keep = g[r][c];
    g[r][c] = b'#';
    let (rows, cols) = (g.len(), g[0].len());
    let ok = (r > 0 && on_board(g, r - 1, c, &w[1..]))
        || (r + 1 < rows && on_board(g, r + 1, c, &w[1..]))
        || (c > 0 && on_board(g, r, c - 1, &w[1..]))
        || (c + 1 < cols && on_board(g, r, c + 1, &w[1..]));
    g[r][c] = keep;
    ok
}

pub fn find_words<'a>(board: &[&str], words: &[&'a str]) -> Vec<&'a str> {
    let mut g: Vec<Vec<u8>> = board.iter().map(|s| s.as_bytes().to_vec()).collect();
    let rows = g.len();
    let mut out: Vec<&'a str> = Vec::new();
    for &word in words {
        if (0..rows).any(|r| (0..g[r].len()).any(|c| on_board(&mut g, r, c, word.as_bytes()))) {
            out.push(word);
        }
    }
    out.sort_unstable();
    out.dedup();
    out
}
