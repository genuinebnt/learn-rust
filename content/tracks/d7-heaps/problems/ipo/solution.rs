use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn find_maximized_capital(k: usize, mut w: u64, profits: &[u64], capital: &[u64]) -> u64 {
    // Projects we can't afford yet, cheapest first.
    let mut locked: BinaryHeap<Reverse<(u64, u64)>> = capital.iter().zip(profits).map(|(&c, &p)| Reverse((c, p))).collect();
    // Projects we can afford, most profitable first.
    let mut affordable: BinaryHeap<u64> = BinaryHeap::new();
    for _ in 0..k {
        while let Some(&Reverse((c, p))) = locked.peek() {
            if c > w {
                break;
            }
            locked.pop();
            affordable.push(p);
        }
        let Some(p) = affordable.pop() else {
            break;
        };
        w += p;
    }
    w
}
