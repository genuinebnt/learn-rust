pub struct Player {
    pub score: u32,
}

/// Moves `points` from player `from` to player `to`.
pub fn transfer(players: &mut [Player], from: usize, to: usize, points: u32) {
    players[to].score += points;
    players[from].score -= points;
}
