pub struct Player {
    pub score: u32,
}

/// Moves `points` from player `from` to player `to`.
pub fn transfer(players: &mut [Player], from: usize, to: usize, points: u32) {
    players[from].score -= points;
    players[to].score += points;
}
