use std::cmp::Reverse;

#[derive(Debug, Clone, PartialEq)]
pub struct File {
    pub name: String,
    pub size: u64,
}

/// The text after the last '.', if any.
fn extension(name: &str) -> Option<&str> {
    name.rsplit_once('.').map(|(_, ext)| ext)
}

/// By extension, ignoring ASCII case (files without one first), then largest first. Ties keep their order.
pub fn sort_files(files: &mut [File]) {
    files.sort_by_cached_key(|f| (extension(&f.name).map(str::to_ascii_lowercase), Reverse(f.size)));
}

/// Most wins first, then fewest losses, then by name. Names are unique.
pub fn leaderboard(players: &mut [(String, u32, u32)]) {
    players.sort_unstable_by(|a, b| b.1.cmp(&a.1).then(a.2.cmp(&b.2)).then_with(|| a.0.cmp(&b.0)));
}

/// Ascending in IEEE 754 total order: -NaN < -inf < … < -0.0 < 0.0 < … < inf < NaN.
pub fn sort_readings(v: &mut [f64]) {
    v.sort_by(|a, b| a.partial_cmp(b).unwrap());
}
