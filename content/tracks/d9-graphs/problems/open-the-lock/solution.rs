use std::collections::VecDeque;

pub fn open_lock(deadends: &[&str], target: &str) -> Option<u32> {
    let code = |s: &str| s.bytes().fold(0usize, |n, b| n * 10 + usize::from(b - b'0'));
    let mut dist: Vec<Option<u32>> = vec![None; 10_000];
    let mut dead = vec![false; 10_000];
    for d in deadends {
        dead[code(d)] = true;
    }
    if dead[0] {
        return None;
    }
    let goal = code(target);
    dist[0] = Some(0);
    let mut queue = VecDeque::from([0usize]);
    while let Some(s) = queue.pop_front() {
        let d = dist[s]?;
        if s == goal {
            return Some(d);
        }
        for place in [1, 10, 100, 1000] {
            let digit = s / place % 10;
            for next_digit in [(digit + 1) % 10, (digit + 9) % 10] {
                let next = s - digit * place + next_digit * place;
                if !dead[next] && dist[next].is_none() {
                    dist[next] = Some(d + 1);
                    queue.push_back(next);
                }
            }
        }
    }
    None
}
