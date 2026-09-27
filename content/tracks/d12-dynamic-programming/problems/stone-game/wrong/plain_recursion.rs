fn lead(p: &[u32]) -> i64 {
    match p {
        [] => 0,
        [x] => *x as i64,
        [first, .., last] => (*first as i64 - lead(&p[1..])).max(*last as i64 - lead(&p[..p.len() - 1])),
    }
}

pub fn stone_game(piles: &[u32]) -> (u64, u64) {
    let total: i64 = piles.iter().map(|&p| p as i64).sum();
    let diff = lead(piles);
    (((total + diff) / 2) as u64, ((total - diff) / 2) as u64)
}
