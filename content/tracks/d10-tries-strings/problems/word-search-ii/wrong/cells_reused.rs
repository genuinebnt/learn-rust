#[derive(Default)]
struct Node {
    children: [Option<Box<Node>>; 26],
    word: Option<usize>,
}

fn dfs<'a>(grid: &[Vec<u8>], r: usize, c: usize, node: &mut Node, depth: usize, words: &[&'a str], out: &mut Vec<&'a str>) {
    let Some(child) = node.children[(grid[r][c] - b'a') as usize].as_deref_mut() else {
        return;
    };
    if let Some(w) = child.word.take() {
        out.push(words[w]);
    }
    if depth == 16 {
        return;
    }
    let (rows, cols) = (grid.len(), grid[0].len());
    if r > 0 {
        dfs(grid, r - 1, c, child, depth + 1, words, out);
    }
    if r + 1 < rows {
        dfs(grid, r + 1, c, child, depth + 1, words, out);
    }
    if c > 0 {
        dfs(grid, r, c - 1, child, depth + 1, words, out);
    }
    if c + 1 < cols {
        dfs(grid, r, c + 1, child, depth + 1, words, out);
    }
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
    let grid: Vec<Vec<u8>> = board.iter().map(|row| row.as_bytes().to_vec()).collect();
    let mut out = Vec::new();
    for r in 0..grid.len() {
        for c in 0..grid[r].len() {
            dfs(&grid, r, c, &mut root, 1, words, &mut out);
        }
    }
    out.sort_unstable();
    out.dedup();
    out
}
