use solution::*;

#[test]
fn shortest_in_grid() {
    check!(r#""...\n.#.\n..." from (0, 0) to (2, 2): length and ends"#, shortest_path(&Grid::from("...\n.#.\n..."), (0, 0), (2, 2)).map(|p| (p.len(), p[0], p[p.len() - 1])), Some((5, (0, 0), (2, 2))));
}

#[test]
fn unreachable_is_none() {
    check!(r#"edges [[1], [2], [], [0]], from 2 to 0"#, shortest_path(&AdjList { edges: vec![vec![1], vec![2], vec![], vec![0]] }, 2, 0), None);
}

#[test]
fn adj_list() {
    check!(r#"edges [[1], [2], [], [0]], start 0"#, reachable(&AdjList { edges: vec![vec![1], vec![2], vec![], vec![0]] }, 0), 3);
}

#[test]
fn edges_are_one_way() {
    check!(r#"edges [[1], [2], [], [0]], start 2"#, reachable(&AdjList { edges: vec![vec![1], vec![2], vec![], vec![0]] }, 2), 1);
}

#[test]
fn grid_from_str() {
    check!(r#""..#\n#..\n##." from (0, 0)"#, reachable(&Grid::from("..#\n#..\n##."), (0, 0)), 5);
}

#[test]
fn grid_from_rows() {
    check!(r##"["..", "#."] from (1, 1)"##, reachable(&Grid::from(vec!["..", "#."]), (1, 1)), 3);
}

#[test]
fn your_graph_too() {
    struct Collatz;
    impl Graph for Collatz {
        type Node = u64;
        fn neighbors(&self, n: &u64) -> Vec<u64> {
            match *n {
                1 => vec![],
                n if n % 2 == 0 => vec![n / 2],
                n => vec![3 * n + 1],
            }
        }
    }
    check!(r#"a Collatz graph defined in the test, start 6"#, reachable(&Collatz, 6), 9);
}
