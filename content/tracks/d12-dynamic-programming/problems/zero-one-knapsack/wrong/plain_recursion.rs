fn best(items: &[(usize, u64)], cap: usize) -> u64 {
    match items {
        [] => 0,
        [(w, v), rest @ ..] => {
            let skip = best(rest, cap);
            if *w <= cap { skip.max(v + best(rest, cap - w)) } else { skip }
        }
    }
}

pub fn knapsack(items: &[(usize, u64)], capacity: usize) -> u64 {
    best(items, capacity)
}
