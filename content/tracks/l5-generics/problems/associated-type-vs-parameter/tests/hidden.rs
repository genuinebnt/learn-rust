use solution::*;

/// A word ladder: nodes are borrowed words, edges join words that differ in one letter.
struct Ladder<'w> {
    words: &'w [&'w str],
}

impl<'w> Graph for Ladder<'w> {
    type Node = &'w str;
    fn neighbors(&self, w: &&'w str) -> Vec<&'w str> {
        self.words
            .iter()
            .copied()
            .filter(|x| x.len() == w.len() && x.chars().zip(w.chars()).filter(|(a, b)| a != b).count() == 1)
            .collect()
    }
}

const WORDS: [&str; 10] = ["cold", "cord", "card", "ward", "warm", "worm", "word", "wore", "core", "bore"];

#[test]
fn path_to_itself() {
    check!(r#"from 1 to 1"#, shortest_path(&AdjList { edges: vec![vec![0], vec![0]] }, 1, 1), Some(vec![1]));
}

#[test]
fn unique_path() {
    check!(r#"edges [[1], [2], [0, 3], []], from 0 to 3"#, shortest_path(&AdjList { edges: vec![vec![1], vec![2], vec![0, 3], vec![]] }, 0, 3), Some(vec![0, 1, 2, 3]));
}

#[test]
fn borrowed_nodes() {
    check!(r#"word ladder cold -> warm"#, shortest_path(&Ladder { words: &WORDS }, "cold", "warm").map(|p| (p.len(), p[0], p[p.len() - 1])), Some((5, "cold", "warm")));
}

#[test]
fn borrowed_nodes_reachable() {
    check!(r#"word ladder from bore"#, reachable(&Ladder { words: &WORDS }, "bore"), 10);
}

#[test]
fn single_node() {
    check!(r#"edges [[]], start 0"#, reachable(&AdjList { edges: vec![vec![]] }, 0), 1);
}

#[test]
fn self_loop_and_duplicates() {
    check!(r#"edges [[0, 1, 1], [0]]"#, reachable(&AdjList { edges: vec![vec![0, 1, 1], vec![0]] }, 0), 2);
}

#[test]
fn cycle() {
    check!(r#"edges [[1], [2], [0]], start 1"#, reachable(&AdjList { edges: vec![vec![1], vec![2], vec![0]] }, 1), 3);
}

#[test]
fn walled_in() {
    check!(r####""###\n#.#\n###" from (1, 1)"####, reachable(&Grid::from("###\n#.#\n###"), (1, 1)), 1);
}

#[test]
fn no_diagonal_moves() {
    check!(r#"".#\n#." from (0, 0)"#, reachable(&Grid::from(".#\n#."), (0, 0)), 1);
}

#[test]
fn ragged_rows() {
    check!(r#"["...", ".", "..."] from (0, 2)"#, reachable(&Grid::from(vec!["...", ".", "..."]), (0, 2)), 7);
}

#[test]
fn grid_neighbors() {
    let g = Grid::from("...\n...\n...");
    check!(r#""...\n...\n..." neighbors of (0, 0) and (1, 1)"#, (g.neighbors(&(0, 0)).len(), g.neighbors(&(1, 1)).len()), (2, 4));
}

#[test]
fn adj_neighbors() {
    check!(r#"edges [[2, 1]] neighbors of 0"#, AdjList { edges: vec![vec![2, 1], vec![], vec![]] }.neighbors(&0), vec![2, 1]);
}

#[test]
fn node_without_copy_or_ord() {
    #[derive(Clone, PartialEq, Eq, Hash)]
    struct Name(String);
    struct Words;
    impl Graph for Words {
        type Node = Name;
        fn neighbors(&self, n: &Name) -> Vec<Name> {
            if n.0.len() < 3 { vec![Name(format!("{}a", n.0))] } else { vec![] }
        }
    }
    check!(r#"a graph whose nodes are Strings in a newtype with no Copy/Ord/Debug"#, reachable(&Words, Name("a".to_string())), 3);
}

fn closure_count(edges: &[Vec<usize>], start: usize) -> usize {
    let n = edges.len();
    let mut reach = vec![vec![false; n]; n];
    for i in 0..n {
        reach[i][i] = true;
        for &j in &edges[i] {
            reach[i][j] = true;
        }
    }
    for k in 0..n {
        for i in 0..n {
            for j in 0..n {
                if reach[i][k] && reach[k][j] {
                    reach[i][j] = true;
                }
            }
        }
    }
    reach[start].iter().filter(|&&b| b).count()
}

fn distance(edges: &[Vec<usize>], from: usize, to: usize) -> Option<usize> {
    let n = edges.len();
    let mut dist = vec![usize::MAX; n];
    dist[from] = 0;
    for _ in 0..n {
        for u in 0..n {
            if dist[u] == usize::MAX {
                continue;
            }
            for &v in &edges[u] {
                dist[v] = dist[v].min(dist[u] + 1);
            }
        }
    }
    (dist[to] != usize::MAX).then_some(dist[to])
}

fn flood(rows: &[String], r: usize, c: usize, seen: &mut Vec<Vec<bool>>) {
    if seen[r][c] {
        return;
    }
    seen[r][c] = true;
    let open = |r: usize, c: usize| rows.get(r).and_then(|row| row.as_bytes().get(c)) == Some(&b'.');
    if r > 0 && open(r - 1, c) {
        flood(rows, r - 1, c, seen);
    }
    if open(r + 1, c) {
        flood(rows, r + 1, c, seen);
    }
    if c > 0 && open(r, c - 1) {
        flood(rows, r, c - 1, seen);
    }
    if open(r, c + 1) {
        flood(rows, r, c + 1, seen);
    }
}

#[test]
fn random_adj_lists_vs_closure() {
    let mut rng = anneal_prelude::Rng::new(4507);
    for _ in 0..300 {
        let n = 1 + rng.below(7);
        let mut edges = Vec::new();
        for _ in 0..n {
            let k = rng.below(3);
            let list: Vec<usize> = rng.vec(k, 0, n as i64 - 1);
            edges.push(list);
        }
        let start = rng.below(n);
        check!(format!("edges = {edges:?}, start = {start}"), reachable(&AdjList { edges: edges.clone() }, start), closure_count(&edges, start));
        let to = rng.below(n);
        let got = shortest_path(&AdjList { edges: edges.clone() }, start, to);
        let valid = got.as_ref().map(|p| p[0] == start && p[p.len() - 1] == to && p.windows(2).all(|w| edges[w[0]].contains(&w[1])));
        check!(format!("edges = {edges:?}, from {start} to {to}"), (got.as_ref().map(|p| p.len() - 1), valid), (distance(&edges, start, to), valid.map(|_| true)));
    }
}

#[test]
fn random_grids_vs_flood_fill() {
    let mut rng = anneal_prelude::Rng::new(4508);
    for _ in 0..300 {
        let h = 1 + rng.below(5);
        let rows: Vec<String> = (0..h).map(|_| { let w = 1 + rng.below(5); rng.string(w, "..#") }).collect();
        let r = rng.below(h);
        let c = rng.below(rows[r].len());
        let mut row = rows[r].clone().into_bytes();
        row[c] = b'.';
        let mut rows = rows;
        rows[r] = String::from_utf8(row).unwrap();
        let mut seen: Vec<Vec<bool>> = rows.iter().map(|row| vec![false; row.len() + 1]).collect();
        seen.push(Vec::new());
        flood(&rows, r, c, &mut seen);
        let want = seen.iter().flatten().filter(|&&b| b).count();
        let refs: Vec<&str> = rows.iter().map(String::as_str).collect();
        check!(format!("rows = {rows:?}, start = ({r}, {c})"), reachable(&Grid::from(refs), (r, c)), want);
    }
}

#[test]
fn scale_open_grid() {
    let row = ".".repeat(600);
    let rows: Vec<&str> = (0..600).map(|_| row.as_str()).collect();
    let g = Grid::from(rows);
    check!("600 x 600 open grid from the corner", reachable(&g, (599, 599)), 360_000);
    check!("600 x 600 open grid, corner to corner", shortest_path(&g, (0, 0), (599, 599)).map(|p| p.len()), Some(1199));
}

#[test]
fn scale_long_chain() {
    let n = 200_000;
    let edges: Vec<Vec<usize>> = (0..n).map(|i| if i + 1 < n { vec![i + 1] } else { vec![] }).collect();
    check!("a chain of 200000 nodes", reachable(&AdjList { edges }, 0), 200_000);
}
