pub fn min_meeting_rooms(meetings: &[(i32, i32)]) -> usize {
    meetings.iter().map(|&(t, _)| meetings.iter().filter(|&&(s, e)| s <= t && t < e).count()).max().unwrap_or(0)
}
