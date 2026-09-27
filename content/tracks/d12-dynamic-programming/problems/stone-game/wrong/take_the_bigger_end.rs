pub fn stone_game(piles: &[u32]) -> (u64, u64) {
    let (mut lo, mut hi) = (0, piles.len());
    let mut scores = [0u64; 2];
    let mut turn = 0;
    while lo < hi {
        if piles[lo] >= piles[hi - 1] {
            scores[turn] += piles[lo] as u64;
            lo += 1;
        } else {
            scores[turn] += piles[hi - 1] as u64;
            hi -= 1;
        }
        turn ^= 1;
    }
    (scores[0], scores[1])
}
