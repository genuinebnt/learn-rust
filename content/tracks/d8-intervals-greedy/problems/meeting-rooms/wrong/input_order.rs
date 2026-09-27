pub fn can_attend_all(meetings: &[(i32, i32)]) -> bool {
    meetings.windows(2).all(|w| w[0].1 <= w[1].0 || w[1].1 <= w[0].0)
}
