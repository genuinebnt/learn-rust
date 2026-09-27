use std::collections::{HashMap, VecDeque};

pub fn sliding_puzzle(board: [[u8; 3]; 2]) -> Option<u32> {
    // Cells 0 1 2 / 3 4 5; the blank at cell i can swap with these cells.
    const NEXT: [&[usize]; 6] = [&[1, 3], &[0, 2, 4], &[1, 5], &[0, 4], &[1, 3, 5], &[2, 4]];
    let goal = [1, 2, 3, 4, 5, 0];
    let start = [board[0][0], board[0][1], board[0][2], board[1][0], board[1][1], board[1][2]];
    let mut dist: HashMap<[u8; 6], u32> = HashMap::from([(start, 0)]);
    let mut queue = VecDeque::from([start]);
    while let Some(state) = queue.pop_front() {
        let d = dist[&state];
        if state == goal {
            return Some(d);
        }
        let blank = state.iter().position(|&t| t == 0).expect("one blank");
        for &cell in NEXT[blank] {
            let mut next = state;
            next.swap(blank, cell);
            if !dist.contains_key(&next) {
                dist.insert(next, d + 1);
                queue.push_back(next);
            }
        }
    }
    None
}
