pub fn can_attend_all(meetings: &[(i32, i32)]) -> bool {
    let n = meetings.len();
    (0..n).all(|i| (i + 1..n).all(|j| meetings[i].1 <= meetings[j].0 || meetings[j].1 <= meetings[i].0))
}
