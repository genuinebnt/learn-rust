use std::collections::{HashMap, VecDeque};

pub fn sliding_puzzle(board: [[u8; 3]; 2]) -> Option<u32> {
    let goal = [1, 2, 3, 4, 5, 0];
    let start = [board[0][0], board[0][1], board[0][2], board[1][0], board[1][1], board[1][2]];
    let mut dist: HashMap<[u8; 6], u32> = HashMap::from([(start, 0)]);
    let mut queue = VecDeque::from([start]);
    while let Some(state) = queue.pop_front() {
        let d = dist[&state];
        if state == goal {
            return Some(d);
        }
        let blank = state.iter().position(|&t| t == 0).unwrap();
        // Treats the board as one row of six, plus up/down.
        for cell in [blank.wrapping_sub(1), blank + 1, blank.wrapping_sub(3), blank + 3] {
            if cell < 6 {
                let mut next = state;
                next.swap(blank, cell);
                if !dist.contains_key(&next) {
                    dist.insert(next, d + 1);
                    queue.push_back(next);
                }
            }
        }
    }
    None
}
