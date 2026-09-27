use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn find_maximized_capital(k: usize, mut w: u64, profits: &[u64], capital: &[u64]) -> u64 {
    let mut locked: BinaryHeap<Reverse<(u64, u64)>> = capital.iter().zip(profits).map(|(&c, &p)| Reverse((c, p))).collect();
    let mut affordable: BinaryHeap<u64> = BinaryHeap::new();
    for _ in 0..k {
        if let Some(&Reverse((c, p))) = locked.peek() {
            if c <= w {
                locked.pop();
                affordable.push(p);
            }
        }
        let Some(p) = affordable.pop() else {
            break;
        };
        w += p;
    }
    w
}
