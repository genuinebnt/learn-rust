use std::cmp::Reverse;

#[derive(Debug, Clone, PartialEq)]
pub struct File {
    pub name: String,
    pub size: u64,
}

/// By extension, ignoring ASCII case (files without one first), then largest first. Ties keep their order.
pub fn sort_files(files: &mut [File]) {
    todo!()
}

/// Most wins first, then fewest losses, then by name. Names are unique.
pub fn leaderboard(players: &mut [(String, u32, u32)]) {
    todo!()
}

/// Ascending in IEEE 754 total order: -NaN < -inf < … < -0.0 < 0.0 < … < inf < NaN.
pub fn sort_readings(v: &mut [f64]) {
    todo!()
}
