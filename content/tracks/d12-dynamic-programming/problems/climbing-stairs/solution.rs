pub fn climb_stairs(n: u32) -> u64 {
    // ways(i) = ways(i - 1) + ways(i - 2): the last move was a 1 or a 2.
    let (mut two_back, mut one_back) = (1u64, 1u64); // ways(0), ways(1)
    for _ in 1..n {
        (two_back, one_back) = (one_back, two_back + one_back);
    }
    one_back
}
