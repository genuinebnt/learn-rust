use solution::*;

#[test]
fn hardest_board() {
    check!(r#"board = [[4,5,0],[1,2,3]]"#, sliding_puzzle([[4, 5, 0], [1, 2, 3]]), Some(21));
}

#[test]
fn blank_first() {
    check!(r#"board = [[0,1,2],[3,4,5]]"#, sliding_puzzle([[0, 1, 2], [3, 4, 5]]), Some(15));
}

#[test]
fn reversed() {
    check!(r#"board = [[5,4,3],[2,1,0]]"#, sliding_puzzle([[5, 4, 3], [2, 1, 0]]), Some(14));
}

#[test]
fn row_end_is_not_next_to_row_start() {
    check!(r#"board = [[1,2,0],[3,4,5]]"#, sliding_puzzle([[1, 2, 0], [3, 4, 5]]), Some(13));
}

#[test]
fn blank_moves_down() {
    check!(r#"board = [[1,2,0],[4,5,3]]"#, sliding_puzzle([[1, 2, 0], [4, 5, 3]]), Some(1));
}

#[test]
fn blank_bottom_left() {
    check!(r#"board = [[1,2,3],[0,4,5]]"#, sliding_puzzle([[1, 2, 3], [0, 4, 5]]), Some(2));
}

#[test]
fn two_tiles_swapped() {
    check!(r#"board = [[2,1,3],[4,5,0]]"#, sliding_puzzle([[2, 1, 3], [4, 5, 0]]), None);
}

#[test]
fn random_vs_brute_force() {
    use std::collections::{HashMap, VecDeque};
    // Brute force: one BFS backwards from the goal over flat boards, with moves found by coordinates.
    let goal = vec![1u8, 2, 3, 4, 5, 0];
    let mut dist: HashMap<Vec<u8>, u32> = HashMap::from([(goal.clone(), 0)]);
    let mut queue = VecDeque::from([goal]);
    while let Some(s) = queue.pop_front() {
        let z = s.iter().position(|&t| t == 0).unwrap();
        let (r, c) = (z / 3, z % 3);
        for (nr, nc) in [(r ^ 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
            if nc < 3 {
                let mut t = s.clone();
                t.swap(z, nr * 3 + nc);
                if !dist.contains_key(&t) {
                    dist.insert(t.clone(), dist[&s] + 1);
                    queue.push_back(t);
                }
            }
        }
    }
    let mut rng = anneal_prelude::Rng::new(953);
    for _ in 0..300 {
        let mut flat = vec![0u8, 1, 2, 3, 4, 5];
        rng.shuffle(&mut flat);
        let board = [[flat[0], flat[1], flat[2]], [flat[3], flat[4], flat[5]]];
        check!(format!("board = {board:?}"), sliding_puzzle(board), dist.get(&flat).copied());
    }
}

#[test]
fn every_board() {
    // All 720 boards: half are solvable, taking 4544 moves in total, 21 at most.
    let mut solvable = 0;
    let (mut total, mut most) = (0, 0);
    for code in 0..46_656u32 {
        let flat: Vec<u8> = (0..6).map(|i| (code / 6u32.pow(i) % 6) as u8).collect();
        if (0..6u8).all(|t| flat.contains(&t)) {
            if let Some(d) = sliding_puzzle([[flat[0], flat[1], flat[2]], [flat[3], flat[4], flat[5]]]) {
                solvable += 1;
                total += d;
                most = most.max(d);
            }
        }
    }
    check!("all 720 boards: (solvable, total moves, most moves)", (solvable, total, most), (360, 4544, 21));
}
