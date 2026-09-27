use solution::*;

#[test]
fn nested() {
    check!(r#"meetings = [(1, 10), (2, 9), (3, 8)]"#, min_meeting_rooms(&[(1, 10), (2, 9), (3, 8)]), 3);
}

#[test]
fn chain() {
    check!(r#"meetings = [(1, 3), (2, 4), (3, 5)]"#, min_meeting_rooms(&[(1, 3), (2, 4), (3, 5)]), 2);
}

#[test]
fn negatives() {
    check!(r#"meetings = [(-10, -5), (-6, 0), (-5, 1)]"#, min_meeting_rooms(&[(-10, -5), (-6, 0), (-5, 1)]), 2);
}

#[test]
fn i32_extremes() {
    check!(r#"meetings = [(MIN, MAX), (0, 1), (1, 2)]"#, min_meeting_rooms(&[(i32::MIN, i32::MAX), (0, 1), (1, 2)]), 2);
}

#[test]
fn i32_touching() {
    check!(r#"meetings = [(MIN, 0), (0, MAX)]"#, min_meeting_rooms(&[(i32::MIN, 0), (0, i32::MAX)]), 1);
}

#[test]
fn leetcode_unsorted() {
    check!(r#"meetings = [(9, 10), (4, 9), (4, 17)]"#, min_meeting_rooms(&[(9, 10), (4, 9), (4, 17)]), 2);
}

#[test]
fn leetcode_shared_end() {
    check!(r#"meetings = [(2, 11), (6, 16), (11, 16)]"#, min_meeting_rooms(&[(2, 11), (6, 16), (11, 16)]), 2);
}

#[test]
fn classic_six() {
    check!(r#"meetings = [(1, 10), (2, 7), (3, 19), (8, 12), (10, 20), (11, 30)]"#, min_meeting_rooms(&[(1, 10), (2, 7), (3, 19), (8, 12), (10, 20), (11, 30)]), 4);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(811);
    for _ in 0..400 {
        let n = rng.below(9);
        let meetings: Vec<(i32, i32)> = (0..n)
            .map(|_| {
                let s = rng.int(-5, 15) as i32;
                let len = rng.int(1, 6) as i32;
                (s, s + len)
            })
            .collect();
        // The busiest moment is always some meeting's start.
        let want = meetings.iter().map(|&(t, _)| meetings.iter().filter(|&&(s, e)| s <= t && t < e).count()).max().unwrap_or(0);
        check!(format!("meetings = {meetings:?}"), min_meeting_rooms(&meetings), want);
    }
}

#[test]
fn scale_200k() {
    let meetings: Vec<(i32, i32)> = (0..200_000).rev().map(|i| (i, i + 1000)).collect();
    check!("(i, i + 1000) for i in 0..200000", min_meeting_rooms(&meetings), 1000);
}
