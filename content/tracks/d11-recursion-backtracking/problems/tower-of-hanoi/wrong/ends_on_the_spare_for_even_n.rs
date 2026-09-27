pub fn hanoi(n: u32) -> Vec<(u8, u8)> {
    fn solve(n: u32, from: u8, spare: u8, to: u8, moves: &mut Vec<(u8, u8)>) {
        if n == 0 {
            return;
        }
        solve(n - 1, from, to, spare, moves);
        moves.push((from, to));
        solve(n - 1, spare, from, to, moves);
    }
    let mut moves = Vec::new();
    // Ignores parity: for even n this ends on peg 1.
    if n % 2 == 0 { solve(n, 0, 2, 1, &mut moves) } else { solve(n, 0, 1, 2, &mut moves) }
    moves
}
