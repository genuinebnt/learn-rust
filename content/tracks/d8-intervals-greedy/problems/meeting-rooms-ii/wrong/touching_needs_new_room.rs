pub fn min_meeting_rooms(meetings: &[(i32, i32)]) -> usize {
    let mut starts: Vec<i32> = meetings.iter().map(|m| m.0).collect();
    let mut ends: Vec<i32> = meetings.iter().map(|m| m.1).collect();
    starts.sort_unstable();
    ends.sort_unstable();
    let (mut in_use, mut most, mut j) = (0usize, 0usize, 0usize);
    for &s in &starts {
        while ends[j] < s {
            in_use -= 1;
            j += 1;
        }
        in_use += 1;
        most = most.max(in_use);
    }
    most
}
