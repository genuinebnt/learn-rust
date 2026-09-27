pub fn can_attend_all(meetings: &[(i32, i32)]) -> bool {
    let mut sorted = meetings.to_vec();
    sorted.sort_unstable_by_key(|m| m.0);
    sorted.windows(2).all(|w| w[0].1 <= w[1].0)
}
