#[derive(Default)]
struct Node {
    children: [Option<Box<Node>>; 26],
    /// The word ending here, until it's found.
    word: Option<usize>,
    /// Words not yet found at or below this node.
    left: usize,
}

/// Searches from cell (r, c), coming from `node`. Returns how many words were found, so callers can prune.
fn dfs<'a>(grid: &mut [Vec<u8>], r: usize, c: usize, node: &mut Node, words: &[&'a str], out: &mut Vec<&'a str>) -> usize {
    let letter = grid[r][c];
    if letter == b'#' {
        return 0; // already on the current path
    }
    let i = (letter - b'a') as usize;
    let Some(child) = node.children[i].as_deref_mut() else {
        return 0;
    };
    let mut found = 0;
    if let Some(w) = child.word.take() {
        out.push(words[w]);
        found += 1;
    }
    grid[r][c] = b'#';
    let (rows, cols) = (grid.len(), grid[0].len());
    if r > 0 && child.left > found {
        found += dfs(grid, r - 1, c, child, words, out);
    }
    if r + 1 < rows && child.left > found {
        found += dfs(grid, r + 1, c, child, words, out);
    }
    if c > 0 && child.left > found {
        found += dfs(grid, r, c - 1, child, words, out);
    }
    if c + 1 < cols && child.left > found {
        found += dfs(grid, r, c + 1, child, words, out);
    }
    grid[r][c] = letter;
    child.left -= found;
    if child.left == 0 {
        node.children[i] = None; // nothing left to find down this branch
    }
    found
}

pub fn find_words<'a>(board: &[&str], words: &[&'a str]) -> Vec<&'a str> {
    let mut unique: Vec<&'a str> = words.to_vec();
    unique.sort_unstable();
    unique.dedup();
    let mut root = Node::default();
    for (w, word) in unique.iter().enumerate() {
        let mut node = &mut root;
        node.left += 1;
        for b in word.bytes() {
            node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
            node.left += 1;
        }
        node.word = Some(w);
    }
    let mut grid: Vec<Vec<u8>> = board.iter().map(|row| row.as_bytes().to_vec()).collect();
    let mut out = Vec::new();
    for r in 0..grid.len() {
        for c in 0..grid[r].len() {
            if root.left > 0 {
                let found = dfs(&mut grid, r, c, &mut root, &unique, &mut out);
                root.left -= found;
            }
        }
    }
    out.sort_unstable();
    out
}
