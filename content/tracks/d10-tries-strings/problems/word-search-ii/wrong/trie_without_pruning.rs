#[derive(Default)]
struct Node {
    children: [Option<Box<Node>>; 26],
    word: Option<usize>,
}

fn dfs<'a>(grid: &mut [Vec<u8>], r: usize, c: usize, node: &mut Node, words: &[&'a str], out: &mut Vec<&'a str>) {
    let letter = grid[r][c];
    if letter == b'#' {
        return;
    }
    let Some(child) = node.children[(letter - b'a') as usize].as_deref_mut() else {
        return;
    };
    if let Some(w) = child.word.take() {
        out.push(words[w]);
    }
    grid[r][c] = b'#';
    let (rows, cols) = (grid.len(), grid[0].len());
    if r > 0 {
        dfs(grid, r - 1, c, child, words, out);
    }
    if r + 1 < rows {
        dfs(grid, r + 1, c, child, words, out);
    }
    if c > 0 {
        dfs(grid, r, c - 1, child, words, out);
    }
    if c + 1 < cols {
        dfs(grid, r, c + 1, child, words, out);
    }
    grid[r][c] = letter;
}

pub fn find_words<'a>(board: &[&str], words: &[&'a str]) -> Vec<&'a str> {
    let mut root = Node::default();
    for (w, word) in words.iter().enumerate() {
        let mut node = &mut root;
        for b in word.bytes() {
            node = node.children[(b - b'a') as usize].get_or_insert_with(Default::default);
        }
        node.word = Some(w);
    }
    let mut grid: Vec<Vec<u8>> = board.iter().map(|row| row.as_bytes().to_vec()).collect();
    let mut out = Vec::new();
    for r in 0..grid.len() {
        for c in 0..grid[r].len() {
            dfs(&mut grid, r, c, &mut root, words, &mut out);
        }
    }
    out.sort_unstable();
    out.dedup();
    out
}
